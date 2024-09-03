package processing.feedforward;

import inference.commons.ScoringFunction;
import inference.nd4j.FeedForwardND4JScoring;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;

import java.util.ArrayList;

public class FeedForwardInferenceFunction
        extends
        ProcessFunction<Tuple2<ArrayList<ArrayList<Float>>, Long>, Tuple3<ArrayList<ArrayList<Float>>, Long, Long>> {
    private final String initialModelPath;
    private final String modelType;
    private ScoringFunction scoringFunction;

    public FeedForwardInferenceFunction(String _initialModelPath, String _modelType) {
        this.initialModelPath = _initialModelPath;
        this.modelType = _modelType;
        System.out.println("init this.modelType=="+this.modelType);
        System.out.println("init this.initialModelPath=="+this.initialModelPath);

        if (this.modelType.equals("nd4j")) {
            this.scoringFunction = new FeedForwardND4JScoring();
            this.scoringFunction.setModelType("feedforward");
        } else
            System.err.println("Unsupported model type!");
    }

    @Override
    public void open(Configuration parameters) throws Exception {
        this.scoringFunction.load(this.initialModelPath);
    }

    @Override
    public void processElement(Tuple2<ArrayList<ArrayList<Float>>, Long> inputBatches, Context context,
                               Collector<Tuple3<ArrayList<ArrayList<Float>>, Long, Long>> collector) throws Exception {
        ArrayList<ArrayList<Float>> result = null;
        if (this.modelType.equals("nd4j")) {
            result = ((FeedForwardND4JScoring) this.scoringFunction).processElement(inputBatches.f0);
        }
        collector.collect(new Tuple3<>(result, inputBatches.f1, System.nanoTime()));

    }
}
