package flink.queries;


import flink.sinks.DummyLatencyCountingSink;
import flink.sources.BidSourceFunction;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple;
import org.apache.flink.api.java.tuple.Tuple1;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.configuration.Configuration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.commons.text.RandomStringGenerator;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.sql.Timestamp;
import java.util.Comparator;

public class Query5mod {

    private static final Logger logger = LoggerFactory.getLogger(Query5.class);

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);
        final float exchangeRate = params.getFloat("exchange-rate", 0.82F);
        String ratelist = params.get("ratelist", "4000_7200000_4000_300000");
        int topsize = params.getInt("topsize", 5);
        int swl_min = params.getInt("swl_min", 60);
        int sws_min = params.getInt("sws_min", 1);
        int wtm_ms = params.getInt("wtm_ms", 1000);
        int extsize = params.getInt("extsize", 1000);

        //  --ratelist 5000_7200000 --psrc 1 --ptrans 1 --pwindow 10 --ptopn 2 --swl_min 60 --sws_min 1 --wtm_ms 1000
        int[] numbers = Arrays.stream(ratelist.split("_"))
                .mapToInt(Integer::parseInt)
                .toArray();
        System.out.println(Arrays.toString(numbers));
        List<List<Integer>> rates = new ArrayList<>();

        for (int i = 0; i < numbers.length - 1; i += 2) {
            rates.add(Arrays.asList(numbers[i], numbers[i + 1]));
        }

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.getConfig().setAutoWatermarkInterval(wtm_ms);

//        env.enableCheckpointing(10000, CheckpointingMode.EXACTLY_ONCE);
//
//        env.getCheckpointConfig().enableUnalignedCheckpoints();
//        env.getCheckpointConfig().setCheckpointTimeout(100000);

        //env.disableOperatorChaining();

        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(5000);

        //final int srcRate = params.getInt("srcRate", 100000);

        DataStream<Bid> bids = env.addSource(new BidSourceFunction(rates))
                .setParallelism(params.getInt("psrc", 1))
                .name("Q1_Source")
                .assignTimestampsAndWatermarks(new TimestampAssigner())
                .name("TimestampAssigner");

        DataStream<Bid> transforming = bids
                .process(new BidTransformFunction(extsize))
                .setParallelism(params.getInt("ptrans", 1))
                .name("Q1_Transform").slotSharingGroup("transform");

        // SELECT B1.auction, count(*) AS num
        // FROM Bid [RANGE 60 MINUTE SLIDE 1 MINUTE] B1
        // GROUP BY B1.auction
        DataStream<String> windowed = transforming.keyBy((KeySelector<Bid, Long>) bid -> bid.auction)
                .window(SlidingEventTimeWindows.of(Time.minutes(swl_min), Time.minutes(sws_min)))
                //.aggregate(new CountBids(), new WindowResultFunciton())
                .aggregate(new BidCountAggregate(), new AuctionWindowFunction())
                .name("Q1_SlidingWindow")
                .setParallelism(params.getInt("pwindow", 2))
                .slotSharingGroup("window");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        DummyLatencyCountingSink sinker = new DummyLatencyCountingSink<>(logger);
        sinker.markerID = "Q1";
        windowed.transform("Q1_Sink", objectTypeInfo, sinker)
                .setParallelism(params.getInt("psink", 1)).slotSharingGroup("sink");

        // execute program
        //env.execute("Nexmark Query5 MOD");
        env.execute("Q1_join");
    }

    private static final class TimestampAssigner implements AssignerWithPeriodicWatermarks<Bid> {
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

    private static final class CountBids implements AggregateFunction<Bid, Long, Long> {

        @Override
        public Long createAccumulator() {
            return 0L;
        }

        @Override
        public Long add(Bid value, Long accumulator) {
            return accumulator + 1;
        }

        @Override
        public Long getResult(Long accumulator) {
            return (accumulator);
        }

        @Override
        public Long merge(Long a, Long b) {
            return a + b;
        }
    }

    public static class AuctionCount {
        public long AuctionID;
        public long windowEnd;
        public long Acount;

        public static AuctionCount of(long AuctionID, long windowEnd, long Acount) {
            AuctionCount AuctionCount = new AuctionCount();
            AuctionCount.AuctionID = AuctionID;
            AuctionCount.windowEnd = windowEnd;
            AuctionCount.Acount = Acount;
            return AuctionCount;
        }
    }

    public static class WindowResultFunciton implements WindowFunction<Long, AuctionCount, Long, TimeWindow> {
        @Override
        public void apply(
                Long key,
                TimeWindow window,
                Iterable<Long> aggregationResult,
                Collector<AuctionCount> collector
        ) throws Exception {
            Long AuctionID = key;
            Long count =aggregationResult.iterator().next();
            collector.collect(AuctionCount.of(AuctionID, window.getEnd(), count));
        }
    }


    private static class BidCountAggregate implements AggregateFunction<Bid, Tuple2<Long, Long>, Tuple2<Long, Long>> {
        /**
         * Create an accumulator for the bid count
         *
         * @return
         */
        @Override
        public Tuple2<Long, Long> createAccumulator() {
            return new Tuple2<>(0L, 0L);
        }

        /**
         * Add a bid to the accumulator
         *
         * @param value
         * @param accumulator
         * @return
         */
        @Override
        public Tuple2<Long, Long> add(Bid value, Tuple2<Long, Long> accumulator) {
            return new Tuple2<>(value.auction, accumulator.f1 + 1);
        }

        /**
         * @param accumulator
         * @return
         * @Description: get the result of the accumulator
         */
        @Override
        public Tuple2<Long, Long> getResult(Tuple2<Long, Long> accumulator) {
            return accumulator;
        }

        /**
         * Merge two accumulators
         *
         * @param a
         * @param b
         * @return
         */
        @Override
        public Tuple2<Long, Long> merge(Tuple2<Long, Long> a, Tuple2<Long, Long> b) {
            return new Tuple2<>(a.f0, a.f1 + b.f1);
        }
    }

    /**
     * @Description: process the highest bid
     */
    private static class AuctionWindowFunction extends ProcessWindowFunction<Tuple2<Long, Long>, String, Long, TimeWindow> {
        /**
         * @param key      The key for which this window is evaluated.
         * @param context  The context in which the window is being evaluated.
         * @param elements The elements in the window being evaluated.
         * @param out      A collector for emitting elements.
         * @Description: iterate over the elements and get the highest bid
         */
        @Override
        public void process(Long key, Context context, Iterable<Tuple2<Long, Long>> elements, Collector<String> out) {
            Tuple2<Long, Long> maxBid = new Tuple2<>(key, Long.MIN_VALUE);
            for (Tuple2<Long, Long> element : elements) {
                if (element.f1 > maxBid.f1) {
                    // get the highest bid
                    maxBid = element;
                }
            }
            out.collect("Auction " + maxBid.f0 + " had the highest number of bids: " + maxBid.f1 + " in the window ending " + context.window().getEnd());
        }
    }


    public static final class BidTransformFunction extends ProcessFunction<Bid, Bid> {
        int extsize;

        public BidTransformFunction(int extsize){
            this.extsize=extsize;
        }

        @Override
        public void processElement(Bid inputBid, Context context,
                                   Collector<Bid> collector) throws Exception {
            long bp=inputBid.price;

            long p = inputBid.price;
//            Do some computation based on bid price and the input extsize (amount of work)
            for (int i = 0; i < this.extsize; i++) {
                p += (long)this.extsize * i;
                p *= p;
            }
            String inputBid_extra = String.valueOf(p);
//            RandomStringGenerator generator = new RandomStringGenerator.Builder()
//                    .withinRange('a', 'z').build();
//            String inputBid_extra = generator.generate(extsize);    //add bidder info

            Bid outputBid=new Bid(inputBid.auction, inputBid.bidder, bp, inputBid.dateTime, inputBid_extra);
            //System.out.println("outputBid.extra="+outputBid.extra.length());
            //System.out.println("outputBid.dateTime="+outputBid.dateTime);
            collector.collect(outputBid);

        }
    }

}
