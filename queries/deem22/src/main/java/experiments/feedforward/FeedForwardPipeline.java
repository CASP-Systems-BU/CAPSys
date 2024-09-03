package experiments.feedforward;

import input.data.feedforward.ImagesDataGeneratorSource;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import processing.feedforward.FeedForwardInferenceFunction;
import processing.feedforward.ImgTransformFunction;
import processing.feedforward.ImgCompressFunction;
import sinks.DummyLatencyCountingSink;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import javax.annotation.Nullable;

import java.util.ArrayList;

public class FeedForwardPipeline {
    private static final Logger logger  = LoggerFactory.getLogger(FeedForwardPipeline.class);

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);
        final int inputRatePerProducer = params.getInt("inputRate", 300);
        final int imgSize = params.getInt("imgSize", 128);
        final int batchSize = params.getInt("batchSize", 1);
        final int experimentTimeInSeconds = params.getInt("experimentTimeInSeconds", 3600);
        final int psrc = params.getInt("psrc", 3);
        final int ptra = params.getInt("ptra", 5);
        final int pcmp = params.getInt("pcmp", 3);
        final int pinf = params.getInt("pinf", 4);
        final int blurstep = params.getInt("blurstep", 16);
        final int warmUpRequestsNum = params.getInt("warmUpRequestsNum", 0);
        final String modelPath = params.get("modelPath", "/home/ubuntu/data/models/");
        String infPath = modelPath+"/feedforward/npy/mnist-fashion/model-1/";
        String ocvPath = modelPath+"/lbpcascade_frontalface.xml";
        // --inputRate 640 --imgSize 128 --batchSize 1 --blurstep 2 --psrc 3 --ptra 6 --pcmp 3 --pinf 3 --modelPath /home/ubuntu/data/models/
        // --inputRate 690 --imgSize 128 --batchSize 1 --blurstep 8 --psrc 3 --ptra 6 --pcmp 3 --pinf 3 --modelPath /home/ubuntu/data/models/
        String ratelist = params.get("dynamicInputRate", "0_0");

        Configuration configuration = new Configuration();
        configuration.setString("taskmanager.memory.process.size", "16GB");    // default is 32GB
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment(configuration);

        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        env.getConfig().setAutoWatermarkInterval(1000);

        //env.disableOperatorChaining();

        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(5000);

        // ========================================== Input Reading ==========================================
        // Read the input data stream
        System.out.println("Input producers: " + psrc);

        DataStream<Tuple2<ArrayList<ArrayList<Float>>, Long>> batches = env
                .addSource(
                        new ImagesDataGeneratorSource(batchSize, experimentTimeInSeconds, warmUpRequestsNum, inputRatePerProducer, imgSize, ratelist))
                .setParallelism(psrc)
                .name("Q3_Source")
                .assignTimestampsAndWatermarks(new TimestampAssigner())
                .name("TimestampAssigner");


        // ========================================== Transform ==========================================

        SingleOutputStreamOperator<Tuple2<ArrayList<ArrayList<Float>>, Long>> transformed = batches
                .process(new ImgTransformFunction(blurstep, imgSize))
                .setParallelism(ptra).slotSharingGroup("tra").name("Q3_Transform");

        // ========================================== Model Scoring ==========================================

        SingleOutputStreamOperator<Tuple2<ArrayList<ArrayList<Float>>, Long>> compressed = transformed
                .process(new ImgCompressFunction(imgSize, 28))
                .setParallelism(pcmp).slotSharingGroup("cmp").name("Q3_Compress");

        // <[scoring-result], in_timestamp, out_timestamp>
        SingleOutputStreamOperator<Tuple3<ArrayList<ArrayList<Float>>, Long, Long>> scoring = compressed
                .process(new FeedForwardInferenceFunction(infPath, "nd4j"))
                .setParallelism(pinf).slotSharingGroup("inf")
                .name("Q3_Inference");

        // ========================================== Benchmarking ==========================================
        //DataStream<Tuple3<ArrayList<ArrayList<Float>>, Long, Long>> merged = scoring.union(transformed);

        // Record timestamp when the scoring is done
//        DataStream<Tuple2<Long, Long>> mapped = scoring.map(new MapFunction<Tuple3<ArrayList<ArrayList<Float>>, Long, Long>, Tuple2<Long, Long>>() {
//            @Override
//            public Tuple2<Long, Long> map(
//                    Tuple3<ArrayList<ArrayList<Float>>, Long, Long> record) {
//                return new Tuple2<>(record.f1, record.f2);
//            }
//        }).setParallelism(pmap).slotSharingGroup("map").name("Map");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        DummyLatencyCountingSink sinker = new DummyLatencyCountingSink<>(logger);
        sinker.markerID = "Q3";
        scoring.transform("Q3_Sink", objectTypeInfo, sinker)
                .setParallelism(params.getInt("psink", 1))
                .slotSharingGroup("sink");

        System.out.println(env.getExecutionPlan());
        env.execute("Q3_inf");
    }

    private static final class TimestampAssigner implements AssignerWithPeriodicWatermarks<Tuple2<ArrayList<ArrayList<Float>>, Long>> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Tuple2<ArrayList<ArrayList<Float>>, Long> element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.f1);
            return element.f1;
        }
    }
}
