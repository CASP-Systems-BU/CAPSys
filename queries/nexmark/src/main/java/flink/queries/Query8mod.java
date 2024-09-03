package flink.queries;


import flink.sinks.DummyLatencyCountingSink;
import flink.sources.AuctionSourceFunction;
import flink.sources.PersonSourceFunction;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Person;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FlatJoinFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.util.Collector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.commons.text.RandomStringGenerator;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

import javax.annotation.Nullable;

public class Query8mod {

    private static final Logger logger = LoggerFactory.getLogger(Query8.class);

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);
        String ratelist = params.getRequired("ratelist");
        int tw_s = params.getInt("tw_s", 10);
        int wtm_ms = params.getInt("wtm_ms", 1000);
        int extsize = params.getInt("extsize", 500);

        //  --ratelist 67000_72000000_38300_72000000 --tw_s 10 --wtm_ms 1000 --p_j 8 --p_ta 3 --p_sa 2 --extsize 300
        int[] numbers = Arrays.stream(ratelist.split("_"))
                .mapToInt(Integer::parseInt)
                .toArray();
        System.out.println(Arrays.toString(numbers));

        List<List<Integer>> auctionSrcRates = new ArrayList<>();
        List<List<Integer>> personSrcRates = new ArrayList<>();

        for (int i = 0; i < numbers.length - 3; i += 4) {
            auctionSrcRates.add(Arrays.asList(numbers[i], numbers[i + 1]));
            personSrcRates.add(Arrays.asList(numbers[i + 2], numbers[i + 3]));
        }

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

//        env.enableCheckpointing(30000, CheckpointingMode.EXACTLY_ONCE);
//
//        env.getCheckpointConfig().enableUnalignedCheckpoints();
//        env.getCheckpointConfig().setCheckpointTimeout(30000);

        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.getConfig().setAutoWatermarkInterval(wtm_ms);

        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(5000);

        env.setParallelism(params.getInt("p_j",1));      //set parallelism for join

        DataStream<Person> persons = env.addSource(new PersonSourceFunction(personSrcRates))
                    .name("Q2_SourcePersons")
                    .slotSharingGroup("sp")
                    .setParallelism(params.getInt("p_sp", 1))
                .assignTimestampsAndWatermarks(new PersonTimestampAssigner())
                    .name("TimestampAssigner")
                    .slotSharingGroup("sp");

        DataStream<Auction> auctions = env.addSource(new AuctionSourceFunction(auctionSrcRates))
                    .name("Q2_SourceAuctions")
                    .slotSharingGroup("sa")
                    .setParallelism(params.getInt("p_sa", 1))
                .assignTimestampsAndWatermarks(new AuctionTimestampAssigner())
                    .name("TimestampAssigner")
                    .slotSharingGroup("sa");

        DataStream<Person> tPersons = persons
                .process(new PersonTransformFunction(extsize))
                .setParallelism(params.getInt("p_tp", 1))
                .name("Q2_TransformPersons").slotSharingGroup("transP");

        DataStream<Auction> tAuctions = auctions
                .process(new AuctionTransformFunction(extsize))
                .setParallelism(params.getInt("p_ta", 1))
                .name("Q2_TransformAuctions").slotSharingGroup("transA");


        // SELECT Rstream(P.id, P.name, A.reserve)
        // FROM Person [RANGE 1 HOUR] P, Auction [RANGE 1 HOUR] A
        // WHERE P.id = A.seller;
        DataStream<Tuple3<Long, String, Long>> joined =
                tPersons.join(tAuctions)
                .where(new KeySelector<Person, Long>() {
                    @Override
                    public Long getKey(Person p) {
                        return p.id;
                    }
                }).equalTo(new KeySelector<Auction, Long>() {
                            @Override
                            public Long getKey(Auction a) {
                                return a.seller;
                            }
                        })
                .window(TumblingEventTimeWindows.of(Time.seconds(tw_s)))
                .apply(new FlatJoinFunction<Person, Auction, Tuple3<Long, String, Long>>() {
                    @Override
                    public void join(Person p, Auction a, Collector<Tuple3<Long, String, Long>> out) {
                        out.collect(new Tuple3<>(p.id, p.name, a.reserve));
                    }
                });
        //.name("window").slotSharingGroup("win");


        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        DummyLatencyCountingSink sinker = new DummyLatencyCountingSink<>(logger);
        sinker.markerID = "Q2";
        joined.transform("Q2_Sink", objectTypeInfo, sinker)
                .setParallelism(params.getInt("psink", 1)).slotSharingGroup("p_sink");

        // execute program
        env.execute("Q2_join");
    }

    private static final class PersonTimestampAssigner implements AssignerWithPeriodicWatermarks<Person> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Person element, long previousElementTimestamp) {
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

    public static final class PersonTransformFunction extends ProcessFunction<Person, Person> {
        int extsize;

        public PersonTransformFunction(int _extrasize){
            this.extsize=_extrasize;
        }

        @Override
        public void processElement(Person inputPerson, Context context,
                                   Collector<Person> collector) throws Exception {
            RandomStringGenerator generator = new RandomStringGenerator.Builder()
                    .withinRange('a', 'z').build();
            String _extra = generator.generate(extsize);    //add bidder info

            Person outputPerson=new Person(
                    inputPerson.id,
                    inputPerson.name,
                    inputPerson.emailAddress,
                    inputPerson.creditCard,
                    inputPerson.city,
                    inputPerson.state,
                    inputPerson.dateTime,
                    _extra);
            //System.out.println("outputPerson.extra="+outputPerson.extra.length());
            //System.out.println("outputPerson.dateTime="+outputPerson.dateTime);
            collector.collect(outputPerson);
        }
    }

    public static final class AuctionTransformFunction extends ProcessFunction<Auction, Auction> {
        int extsize;

        public AuctionTransformFunction(int _extrasize){
            this.extsize=_extrasize;
        }

        @Override
        public void processElement(Auction inputAuction, Context context,
                                   Collector<Auction> collector) throws Exception {
            RandomStringGenerator generator = new RandomStringGenerator.Builder()
                    .withinRange('a', 'z').build();
            String _extra = generator.generate(extsize);    //add bidder info

            Auction outputAuction=new Auction(
                    inputAuction.id,
                    inputAuction.itemName,
                    inputAuction.description,
                    inputAuction.initialBid,
                    inputAuction.reserve,
                    inputAuction.dateTime,
                    inputAuction.expires,
                    inputAuction.seller,
                    inputAuction.category,
                    _extra);
            //System.out.println("outputAuction.extra="+outputAuction.extra.length());
            //System.out.println("outputAuction.dateTime="+outputAuction.dateTime);
            collector.collect(outputAuction);
        }
    }

}