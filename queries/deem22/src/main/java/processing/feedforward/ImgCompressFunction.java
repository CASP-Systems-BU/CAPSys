package processing.feedforward;

import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;

import java.util.ArrayList;

public class ImgCompressFunction
        extends
        ProcessFunction<Tuple2<ArrayList<ArrayList<Float>>, Long>, Tuple2<ArrayList<ArrayList<Float>>, Long>> {
    private Integer OutputSize;
    private Integer InputSize;

    public ImgCompressFunction(Integer _InputSize, Integer _OutputSize) {
        this.InputSize = _InputSize;
        this.OutputSize = _OutputSize;
    }

    public int get1didx(int x, int y, int imgsize){
        int res=x*imgsize+y;
        if(res<0)
            res+=imgsize*imgsize;
        res=res%(imgsize*imgsize);
        return(res);
    }

    @Override
    public void processElement(Tuple2<ArrayList<ArrayList<Float>>, Long> inputBatches, Context context,
                               Collector<Tuple2<ArrayList<ArrayList<Float>>, Long>> collector) throws Exception {
        ArrayList<ArrayList<Float>> result = new ArrayList<>();
        int inputSize = inputBatches.f0.get(0).size();
        int batchSize = inputBatches.f0.size();
        int outputSize = Math.min(OutputSize*OutputSize, inputSize);

        for(int i=0; i<batchSize;i++){
            ArrayList<Float> tmp = new ArrayList<>();
            for(int dx=0; dx<OutputSize; dx++){
                for(int dy=0; dy<OutputSize; dy++){
                    int tx=(int) dx*InputSize/OutputSize;
                    int ty=(int) dy*InputSize/OutputSize;
                    tmp.add(inputBatches.f0.get(i).get(get1didx(tx, ty, InputSize)));
                }
            }
            result.add(tmp);
        }

        collector.collect(new Tuple2<>(result, inputBatches.f1));

    }
}
