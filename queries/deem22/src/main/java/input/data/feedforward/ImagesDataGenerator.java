package input.data.feedforward;

import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.examples.utils.ThrottledIterator;

import java.io.Serializable;
import java.util.*;
import java.util.stream.*;

public class ImagesDataGenerator implements Iterator<Tuple2<ArrayList<ArrayList<Float>>, Long>>, Serializable {
    private static final Random rand = new Random();
    private final int IMAGE_SIZE;

    private final int batchSize;
    private final int experimentTime;

    private int warmupRequestsNum;
    private boolean finishedWarmUp;
    private long startTime;

    ImagesDataGenerator(int batchSize, int experimentTimeInSeconds, int warmupRequestsNum, int _imgsize) {
        this.IMAGE_SIZE = _imgsize;
        this.batchSize = batchSize;
        this.experimentTime = experimentTimeInSeconds * 1000;
        this.warmupRequestsNum = warmupRequestsNum;

        this.finishedWarmUp = false;
    }

    @Override
    public boolean hasNext() {
        if (!finishedWarmUp) {
            warmupRequestsNum--;
            if (warmupRequestsNum < 0) {
                finishedWarmUp = true;
                this.startTime = System.currentTimeMillis();
            }
        } else {
            if (System.currentTimeMillis() - startTime > experimentTime)
                return false;
        }
        return true;
    }

    @Override
    public Tuple2<ArrayList<ArrayList<Float>>, Long> next() {
        ArrayList<ArrayList<Float>> batch = new ArrayList<>();
        for (int imgNum = 0; imgNum < this.batchSize; imgNum++) {
            // generate 0-filled image
            ArrayList<Float> newImage = new ArrayList<Float>(Collections.nCopies(IMAGE_SIZE * IMAGE_SIZE, 6.0f));
//            int randomValIndex = rand.nextInt(IMAGE_SIZE * IMAGE_SIZE);
//            newImage.set(randomValIndex, rand.nextFloat());
            // append the new image to the batch
            batch.add(newImage);
        }
        return new Tuple2<>(batch, System.nanoTime());
    }

    public static DataStream<Tuple2<ArrayList<ArrayList<Float>>, Long>> getThrottledSource(
            StreamExecutionEnvironment env,
            long inputRate, int batchSize,
            int experimentTimeInSeconds,
            int warmupRequestsNum,
            int _imgsize) {
        return env.fromCollection(
                new ThrottledIterator<>(new ImagesDataGenerator(batchSize, experimentTimeInSeconds, warmupRequestsNum, _imgsize),
                                        inputRate),
                TypeInformation.of(new TypeHint<Tuple2<ArrayList<ArrayList<Float>>, Long>>() {}));
    }

    public static DataStream<Tuple2<ArrayList<ArrayList<Float>>, Long>> getSource(StreamExecutionEnvironment env,
                                                                                  int batchSize,
                                                                                  int experimentTimeInSeconds,
                                                                                  int warmupRequestsNum,
                                                                                  int _imgsize) {
        return env.fromCollection(new ImagesDataGenerator(batchSize, experimentTimeInSeconds, warmupRequestsNum, _imgsize),
                                  TypeInformation.of(new TypeHint<Tuple2<ArrayList<ArrayList<Float>>, Long>>() {}));
    }
}
