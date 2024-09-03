package experiments.feedforward;

import input.data.feedforward.ImagesDataGeneratorSource;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import processing.feedforward.ImgSimpleFunction;
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

public class SimplePipeline {
    private static final Logger logger  = LoggerFactory.getLogger(FeedForwardPipeline.class);

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);
        final int inputRatePerProducer = params.getInt("inputRate", 620);
        final int imgSize = params.getInt("imgSize", 128);
        final int batchSize = params.getInt("batchSize", 1);
        final int experimentTimeInSeconds = params.getInt("experimentTimeInSeconds", 3600);
        final int psrc = params.getInt("psrc", 3);
        final int pt1 = params.getInt("pt1", 6);
        final int pt2 = params.getInt("pt2", 3);
        final int pt3 = params.getInt("pt3", 3);
        final int warmUpRequestsNum = params.getInt("warmUpRequestsNum", 0);
        // --inputRate 640 --imgSize 128 --batchSize 1 --psrc 2 --pt1 4 --pt2 2 --pt3 2
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
        System.out.println("Input rate per producer: " + inputRatePerProducer);

        DataStream<Tuple2<ArrayList<ArrayList<Float>>, Long>> batches = env
                .addSource(
                        new ImagesDataGeneratorSource(batchSize, experimentTimeInSeconds, warmUpRequestsNum, inputRatePerProducer, imgSize, ratelist))
                .setParallelism(psrc)
                .name("Source")
                .assignTimestampsAndWatermarks(new TimestampAssigner())
                .name("TimestampAssigner");

        SingleOutputStreamOperator<Tuple2<ArrayList<ArrayList<Float>>, Long>> transformed = batches
                .process(new ImgSimpleFunction(imgSize*imgSize))
                .setParallelism(pt1).slotSharingGroup("t1").name("Transform");

        SingleOutputStreamOperator<Tuple2<ArrayList<ArrayList<Float>>, Long>> compressed = transformed
                .process(new ImgSimpleFunction(28*28))
                .setParallelism(pt2).slotSharingGroup("t2").name("Compress");

        SingleOutputStreamOperator<Tuple2<ArrayList<ArrayList<Float>>, Long>> scoring = compressed
                .process(new ImgSimpleFunction(1*1))
                .setParallelism(pt3).slotSharingGroup("t3").name("Inference");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        scoring.transform("Sink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(1)
                .slotSharingGroup("sink");

        System.out.println(env.getExecutionPlan());
        env.execute("ML Inference Simplified");
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
