package processing.feedforward;

import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;

import java.util.*;

public class ImgSimpleFunction
        extends
        ProcessFunction<Tuple2<ArrayList<ArrayList<Float>>, Long>, Tuple2<ArrayList<ArrayList<Float>>, Long>> {
    private Integer OutputSize;

    public ImgSimpleFunction(Integer _OutputSize) {
        this.OutputSize = _OutputSize;
    }

    @Override
    public void processElement(Tuple2<ArrayList<ArrayList<Float>>, Long> inputBatches, Context context,
                               Collector<Tuple2<ArrayList<ArrayList<Float>>, Long>> collector) throws Exception {
        ArrayList<ArrayList<Float>> result = new ArrayList<>();
        int inputSize = inputBatches.f0.get(0).size();
        int batchSize = inputBatches.f0.size();

        if(inputSize==OutputSize){
            collector.collect(inputBatches);
        }
        else {
            for (int i = 0; i < batchSize; i++) {
                ArrayList<Float> tmp = new ArrayList<Float>(Collections.nCopies(OutputSize, 6.0f));
                result.add(tmp);
            }
            collector.collect(new Tuple2<>(result, inputBatches.f1));
        }
    }
}
