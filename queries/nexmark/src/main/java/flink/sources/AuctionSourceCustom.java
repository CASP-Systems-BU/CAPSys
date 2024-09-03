/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package flink.sources;

import org.apache.beam.sdk.nexmark.NexmarkConfiguration;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.AuctionGenerator;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.runtime.state.FunctionInitializationContext;
import org.apache.flink.runtime.state.FunctionSnapshotContext;
import org.apache.flink.streaming.api.checkpoint.CheckpointedFunction;
import org.apache.flink.streaming.api.functions.source.RichParallelSourceFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Date;
import java.util.List;
import java.util.Random;

/**
 * A ParallelSourceFunction that generates Nexmark Person data
 * https://github.com/pentium3/beam/blob/master/sdks/java/testing/nexmark/src/main/java/org/apache/beam/sdk/nexmark/sources/generator/model/AuctionGenerator.java
 */
public class AuctionSourceCustom extends RichParallelSourceFunction<Auction> implements CheckpointedFunction {

    private static final Logger LOG = LoggerFactory.getLogger(AuctionSourceCustom.class);

    private GeneratorConfig config;

    private final List<List<Integer>> rates;
    Integer totalTime;
    private volatile boolean running = true;
    private Long eventsCountSoFar;
    private Long time;
    private ListState<Long> stateAuction;
    private ListState<Long> stateEventsCountSoFar;
    private ListState<Long> stateBaseTime;
    private Long auctionIDRange=80000L;
    private Long baseTime;
    private Long rangeTimeUpper=10L;
    private Long rangeTimeLower=6L;
    private Long sellerIDRange=1000L;
    private Long expireInterval=100L;

    public AuctionSourceCustom(List<List<Integer>> srcRate) {
        NexmarkConfiguration manual_config = new NexmarkConfiguration();
        manual_config.hotAuctionRatio = 1;
        manual_config.hotBiddersRatio = 1;
        manual_config.hotSellersRatio = 1;
        this.config = new GeneratorConfig(
                manual_config,
                1,
                1000L,
                0,
                1);
        this.rates = srcRate;
        totalTime = sumTime();
    }

    private void updateRates() {
        Long curTime = System.currentTimeMillis() - time;
        int toRemove = 0;
        for (int i = 0; i < rates.size(); i++) {
            int currentDuration = this.rates.get(i).get(1);
            if (curTime > currentDuration) {
                curTime -= currentDuration;
                toRemove++;
            } else {
                List<Integer> rateToChange = this.rates.get(i);
                rateToChange.set(1, (int) (rateToChange.get(1) - curTime));
                this.rates.set(i, rateToChange);
                break; // Do this only once
            }
        }
        if (toRemove > 0) {
            this.rates.subList(0, toRemove).clear();
        }
    }

    private int sumTime() {
        int result = 0;
        assert this.rates != null;
        for (List<Integer> rate : this.rates) {
            result += rate.get(1);
        }
        return result;
    }

    @Override
    public void run(SourceContext<Auction> ctx) throws Exception {
        for (int currentRateCount = 0; currentRateCount < this.rates.size(); currentRateCount++) {
            int currentRate = this.rates.get(currentRateCount).get(0);
            int currentDuration = this.rates.get(currentRateCount).get(1);
            Date finishTime = new Date();

            while (running && new Date().getTime() - finishTime.getTime() < currentDuration) {
                long emitStartTime = System.currentTimeMillis();

                for (int i = 0; i < currentRate; i++) {
                    long nextId = nextId();
                    Random rnd = new Random();

                    // When, in event time, we should generate the event. Monotonic.
                    long eventTimestamp =
                            config.timestampAndInterEventDelayUsForEvent(
                                    config.nextEventNumber(eventsCountSoFar)).getKey();

//                    Auction auction = AuctionGenerator.nextAuction(eventsCountSoFar, nextId, rnd, eventTimestamp, config);
                    String name = nextString(rnd, 20);
                    String desc = nextString(rnd, 100);
                    String extra = nextString(rnd, 20);
                    long initialBid=0L;
                    long reserve=0L;
                    long category=0L;
                    //long id = (eventsCountSoFar+1)%auctionIDRange;
                    long id = 1 + (long)(rnd.nextDouble() * auctionIDRange);
                    long timestamp = baseTime + rangeTimeLower + (long) ((rangeTimeUpper - rangeTimeLower + 1) * rnd.nextDouble());
                    //System.out.println("AuctionSourceCustom baseTime==== "+baseTime);
                    baseTime = timestamp;
                    long expires = timestamp+expireInterval;
                    long seller = 1 + (long)(rnd.nextDouble() * sellerIDRange);
//                    long seller = (eventsCountSoFar+1)%sellerIDRange;

                    Auction auction = new Auction(id, name, desc, initialBid, reserve, timestamp, expires, seller, category, extra);
                    ctx.collect(auction);

                    // https://github.com/nexmark/nexmark/blob/master/nexmark-flink/src/main/java/com/github/nexmark/flink/generator/model/AuctionGenerator.java#L44
                    eventsCountSoFar++;
                }

                // Sleep for the rest of timeslice if needed
                long emitTime = System.currentTimeMillis() - emitStartTime;
                if (emitTime < 1000) {
                    Thread.sleep(1000 - emitTime);
                }
            }
        }
    }

    @Override
    public void cancel() {
        running = false;
    }

    private long nextId() {
        return config.firstEventId + config.nextAdjustedEventNumber(eventsCountSoFar);
    }

    @Override
    public void snapshotState(FunctionSnapshotContext context) throws Exception {
        stateEventsCountSoFar.clear();
        stateEventsCountSoFar.add(eventsCountSoFar);
        stateBaseTime.clear();
        stateBaseTime.add(baseTime);
    }

    @Override
    public void initializeState(FunctionInitializationContext context) throws Exception {
        stateAuction = context.getOperatorStateStore().getListState(new ListStateDescriptor<>(
                "stateAuction",
                Long.class));
        stateEventsCountSoFar = context.getOperatorStateStore()
                .getListState(new ListStateDescriptor<>("stateEventsCountSoFar",  Long.class));
        stateBaseTime = context.getOperatorStateStore()
                .getListState(new ListStateDescriptor<>("stateBaseTime",  Long.class));

        for (Long l : stateAuction.get()) {
            time = l;
        }
        if (time == null) {
            time = System.currentTimeMillis();
            System.out.println("AuctionSourceCustom:  Initialized time value state");
        } else {
            System.out.println("AuctionSourceCustom:  Value state recovered.. time="+time);
        }

        for (Long l : stateEventsCountSoFar.get()) {
            eventsCountSoFar = l;
        }
        if (eventsCountSoFar == null) {
            eventsCountSoFar=0L;
            System.out.println("AuctionSourceCustom:  Initialized eventsCountSoFar value state");
        } else {
            System.out.println("AuctionSourceCustom:  Value state recovered.. eventsCountSoFar="+eventsCountSoFar);
        }

        for (Long l : stateBaseTime.get()) {
            baseTime = l;
        }
        if (baseTime == null) {
            baseTime=1L;
            System.out.println("AuctionSourceCustom:  Initialized baseTime value state");
        } else {
            System.out.println("AuctionSourceCustom:  Value state recovered.. baseTime="+baseTime);
        }
//        updateRates();
        System.out.println("AuctionSourceCustom:  Updated rates, " + rates.toString());
    }

    public static String nextString(Random random, int maxLength) {
        int len = 3 + random.nextInt(maxLength - 3);
        StringBuilder sb = new StringBuilder();
        while (len-- > 0) {
            if (random.nextInt(13) == 0) {
                sb.append(' ');
            } else {
                sb.append((char) ('a' + random.nextInt(26)));
            }
        }
        return sb.toString().trim();
    }
}
