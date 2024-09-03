package processing.feedforward;

import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;

import java.util.*;

public class ImgTransformFunction
        extends
        ProcessFunction<Tuple2<ArrayList<ArrayList<Float>>, Long>, Tuple2<ArrayList<ArrayList<Float>>, Long>> {
    private final int step;
    private final int imgSize;

    public int getidx(int x, int y, int imgsize){
        int res=x*imgsize+y;
        if(res<0)
            res+=imgsize*imgsize;
        res=res%(imgsize*imgsize);
        return(res);
    }

    public ImgTransformFunction(int step, int imgSize) {
        this.step=step;
        this.imgSize=imgSize;
    }

    @Override
    public void processElement(Tuple2<ArrayList<ArrayList<Float>>, Long> inputBatches, Context context,
                               Collector<Tuple2<ArrayList<ArrayList<Float>>, Long>> collector) throws Exception {
        ArrayList<ArrayList<Float>> result = new ArrayList<>();
        int inputSize = inputBatches.f0.get(0).size();
        int batchSize = inputBatches.f0.size();

        for(int bi=0; bi<batchSize; bi++){
            ArrayList<Float> inputImg = inputBatches.f0.get(bi);
            for (int i=0;i<this.imgSize;i+=this.step){
                for(int j=0;j<this.imgSize;j+=this.step){
                    ArrayList<Integer> idxavg = new ArrayList<>(Arrays.asList(getidx(i,j,this.imgSize),
                            getidx(i-1,j-1,this.imgSize),
                            getidx(i-1,j,this.imgSize),
                            getidx(i-1,j+1,this.imgSize),
                            getidx(i,j-1,this.imgSize),
                            getidx(i,j+1,this.imgSize),
                            getidx(i+1,j-1,this.imgSize),
                            getidx(i+1,j,this.imgSize),
                            getidx(i+1,j+1,this.imgSize)
                    ));
                    // https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html
                    float res=0.0f;
                    for(int k : idxavg){
                        res+=inputImg.get(k);
                    }
                    res=res/9;
                    inputImg.set(i*this.imgSize+j, res);
                }
            }
            result.add(inputImg);
        }

        collector.collect(new Tuple2<>(result, inputBatches.f1));

    }
}
