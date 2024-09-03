package flink.queries;

import flink.sinks.DummyLatencyCountingSink;
import flink.sources.AuctionSourceCustom;
import flink.sources.BidSourceCustom;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.state.MapState;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.streaming.api.functions.co.CoProcessFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.api.java.typeutils.TupleTypeInfo;
import org.apache.flink.util.Collector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.LinkedList;
import java.util.Properties;


/**
 * Query 6: Average Selling Price by Seller
 * SELECT Istream(AVG(Q.final), Q.seller)
 * FROM (SELECT Rstream(MAX(B.price) AS final, A.seller)
 * FROM Auction A [ROWS UNBOUNDED], Bid B [ROWS UNBOUNDED]
 * WHERE A.id=B.auction AND B.datetime < A.expires AND A.expires < CURRENT_TIME
 * GROUP BY A.id, A.seller) [PARTITION BY A.seller ROWS 10] Q
 * GROUP BY Q.seller;
 */

/**
 * @@author arkashjain
 * @@since 2024
 */
public class Query6 {
    private static final Logger logger = LoggerFactory.getLogger(Query6.class);

    public static void main(String[] args) throws Exception {
        final ParameterTool params = ParameterTool.fromArgs(args);
        String ratelist = params.get("ratelist", "67000_72000000_38300_72000000");
        // Time parameters
        final int SECOND = 1000;
        final int MINUTE = 60 * SECOND;
        final int HOUR = 60 * MINUTE;
        final int LATENCY_INTERVAL = 5000;

        // Flink environment setup
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        // Set the EventTime characteristic
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.getConfig().setAutoWatermarkInterval(1000);
        // Checkpointing configuration
        //int checkpointinginterval = 10 * MINUTE;
        //env.enableCheckpointing(checkpointinginterval, CheckpointingMode.EXACTLY_ONCE);

        env.getConfig().setLatencyTrackingInterval(LATENCY_INTERVAL);
        env.getConfig().setGlobalJobParameters(params);

        //  --ratelist 127000_72000000_68300_72000000 --psa 1 --psb 1 --pj 22 --pagg 6 --psink 1
        int[] numbers = Arrays.stream(ratelist.split("_"))
                .mapToInt(Integer::parseInt)
                .toArray();
        System.out.println(Arrays.toString(numbers));

        List<List<Integer>> auctionSrcRates = new ArrayList<>();
        List<List<Integer>> bidsSrcRates = new ArrayList<>();

        for (int i = 0; i < numbers.length - 3; i += 4) {
            auctionSrcRates.add(Arrays.asList(numbers[i], numbers[i + 1]));
            bidsSrcRates.add(Arrays.asList(numbers[i + 2], numbers[i + 3]));
        }

        DataStream<Auction> auctions = env.addSource(new AuctionSourceCustom(auctionSrcRates))
                .name("Q5_SourceAuction")
                .slotSharingGroup("psa")
                .setParallelism(params.getInt("psa", 1))
            .assignTimestampsAndWatermarks(new AuctionTimestampAssigner())
                .name("TimestampAssigner")
                .slotSharingGroup("psa");
        DataStream<Bid> bids = env.addSource(new BidSourceCustom(bidsSrcRates))
                .name("Q5_SourceBid")
                .slotSharingGroup("psb")
                .setParallelism(params.getInt("psb", 1))
            .assignTimestampsAndWatermarks(new BidTimestampAssigner())
                .name("TimestampAssigner")
                .slotSharingGroup("psb");

        // Key auctions and bids by their respective IDs
        KeyedStream<Auction, Long> keyedAuctions = auctions
                .keyBy(
                        new KeySelector<Auction, Long>() {
                            @Override
                            public Long getKey(Auction auction) throws Exception {
                                return auction.id;
                            }
                        }
                );

        KeyedStream<Bid, Long> keyedBids = bids
                .keyBy(new KeySelector<Bid, Long>() {
                    @Override
                    public Long getKey(Bid bid) throws Exception {
                        return bid.auction;
                    }
                });

        // Emit a joint stream of Auctions and Bids keyed by the auction ID
        DataStream<Tuple2<Long, Long>> joinedStream = keyedBids.connect(keyedAuctions)
                .process(new JoinBidsWithAuctions())
                .name("Q5_JoinBidsWithAuctions")
                .slotSharingGroup("pj")
                .setParallelism(params.getInt("pj", 2));

        KeyedStream<Tuple2<Long, Long>, Long> keyedJoinedStream = joinedStream
                .keyBy(new KeySelector<Tuple2<Long, Long>, Long>() {
                    @Override
                    public Long getKey(Tuple2<Long, Long> value) throws Exception {
                        return value.f1;
                    }
                });

        DataStream<Tuple2<Long, Double>> avgPriceStream = keyedJoinedStream
                .process(new AverageAggregate())
                .name("Q5_AggregateFunction")
                .slotSharingGroup("pagg")
                .setParallelism(params.getInt("pagg", 1));

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        DummyLatencyCountingSink sinker = new DummyLatencyCountingSink<>(logger);
        sinker.markerID = "Q5";
        avgPriceStream.transform("Q5_Sink", objectTypeInfo, sinker)
                .setParallelism(params.getInt("psink", 1)).slotSharingGroup("p_sink");

        env.execute("Q5_aggregate");
    }


    /**
     * @Description: This function joins the Auction and Bid streams and emits the bids that arrived before the auction ended.
     * The function also buffers the bids that arrived after the auction ended.
     * @@implNote The function uses a CoProcessFunction to join the Auction and Bid streams.
     * @@hidden
     */
    public static class JoinBidsWithAuctions extends CoProcessFunction<Bid, Auction, Tuple2<Long, Long>> {
        private ListState<Bid> bidState;
        private ListState<Auction> auctionState;

        private long temCnt=0;

        @Override
        public void open(Configuration config) {
            ListStateDescriptor<Auction> auctionStateDescriptor = new ListStateDescriptor<>(
                    "auctionState", // state name
                    TypeInformation.of(new TypeHint<Auction>() {})
            );
            auctionState = getRuntimeContext().getListState(auctionStateDescriptor);

            ListStateDescriptor<Bid> bidStateDescriptor = new ListStateDescriptor<>(
                    "bidState",
                    TypeInformation.of(new TypeHint<Bid>() {})
            );
            bidState = getRuntimeContext().getListState(bidStateDescriptor);
        }

        @Override
        public void processElement1(Bid bid, Context ctx, Collector<Tuple2<Long, Long>> out) throws Exception {
            bidState.add(bid);
            System.out.println("incoming Bid ==== "+bid);
        }

        @Override
        public void processElement2(Auction auction, Context ctx, Collector<Tuple2<Long, Long>> out) throws Exception {
            auctionState.add(auction);
            ctx.timerService().registerEventTimeTimer(auction.expires);
            System.out.println("incoming Auction ==== "+auction);
        }

        @Override
        public void onTimer(long timestamp, OnTimerContext ctx, Collector<Tuple2<Long, Long>> out) throws Exception {

            long currentTime = ctx.timerService().currentWatermark();

            List<Auction> updatedAuctionState = new ArrayList<>();
            List<Bid> updatedBidState=null;

            for(Auction auction : auctionState.get()){
                if(auction.expires==timestamp){
                    long maxBidPrice=0;
                    updatedBidState = new ArrayList<>();
                    for (Bid bid : bidState.get()) {
                        if (auction.expires >= bid.dateTime) {
                            if(bid.price>maxBidPrice){
                                maxBidPrice=bid.price;
                            }
                        }
                        else{
                            updatedBidState.add(bid);
                        }
                    }
                    out.collect(new Tuple2<>(maxBidPrice, auction.seller));
                }
                else{
                    updatedAuctionState.add(auction);
                }
            }

            //auctionState.clear();
            auctionState.update(updatedAuctionState);
            //bidState.clear();
            if(updatedBidState != null) {
                bidState.update(updatedBidState);
            }
        }
    }

    public static class AverageAggregate extends ProcessFunction<Tuple2<Long, Long>, Tuple2<Long, Double>> {
        private ListState<Long> avglist;

        @Override
        public void open(Configuration config) {
            ListStateDescriptor<Long> avglistDescriptor = new ListStateDescriptor<>(
                    "avglist",
                    TypeInformation.of(new TypeHint<Long>() {})
            );
            avglist = getRuntimeContext().getListState(avglistDescriptor);
        }

        @Override
        public void processElement(Tuple2<Long, Long> in, Context context,
                                   Collector<Tuple2<Long, Double>> out) throws Exception {

            Iterable<Long> elements = avglist.get();
            LinkedList<Long> elementsList = new LinkedList<>();
            elements.forEach(elementsList::add);
            elementsList.add(in.f1);
            if (elementsList.size() > 300) {
                elementsList.removeFirst();
            }
            avglist.update(elementsList);

            double sum = 0;
            for (Long v : elementsList) {
                sum += v;
            }
            double avg = sum / elementsList.size();

            out.collect(new Tuple2<>(in.f1, avg));
        }
    }




    private static final class BidTimestampAssigner implements AssignerWithPeriodicWatermarks<Bid> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Bid element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

    private static final class AuctionTimestampAssigner implements AssignerWithPeriodicWatermarks<Auction> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Auction element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

}
