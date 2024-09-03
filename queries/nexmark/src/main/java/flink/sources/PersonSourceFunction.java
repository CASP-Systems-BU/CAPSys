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
import org.apache.beam.sdk.nexmark.model.Person;
import org.apache.beam.sdk.nexmark.sources.generator.GeneratorConfig;
import org.apache.beam.sdk.nexmark.sources.generator.model.PersonGenerator;
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

;

/**
 * A ParallelSourceFunction that generates Nexmark Person data
 */
public class PersonSourceFunction extends RichParallelSourceFunction<Person> implements CheckpointedFunction {

    private static final Logger LOG = LoggerFactory.getLogger(PersonSourceFunction.class);
    private final GeneratorConfig config = new GeneratorConfig(NexmarkConfiguration.DEFAULT, 1, 1000L, 0, 1);
    private final List<List<Integer>> rates;
    Integer totalTime;
    private volatile boolean running = true;
    private Long eventsCountSoFar;
    private Long time;
    private ListState<Long> statePerson;
    private ListState<Long> stateEventsCountSoFar;

    public PersonSourceFunction(List<List<Integer>> srcRate) {
        this.rates = srcRate;
        totalTime = sumTime();
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
    public void run(SourceContext<Person> ctx) throws Exception {
        for (int currentRateCount = 0; currentRateCount < this.rates.size(); currentRateCount++) {
            int currentRate = this.rates.get(currentRateCount).get(0);
            int currentDuration = this.rates.get(currentRateCount).get(1);
            Date finishTime = new Date();

            while (running && new Date().getTime() - finishTime.getTime() < currentDuration) {
                long emitStartTime = System.currentTimeMillis();

                for (int i = 0; i < currentRate; i++) {
                    long nextId = nextId();
                    Random rnd = new Random(nextId);

                    // When, in event time, we should generate the event. Monotonic.
                    long eventTimestamp =
                            config.timestampAndInterEventDelayUsForEvent(config.nextEventNumber(eventsCountSoFar)).getKey();

                    ctx.collect(PersonGenerator.nextPerson(nextId, rnd, eventTimestamp, config));
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

    @Override
    public void snapshotState(FunctionSnapshotContext context) throws Exception {
        stateEventsCountSoFar.clear();
        stateEventsCountSoFar.add(eventsCountSoFar);
    }

    @Override
    public void initializeState(FunctionInitializationContext context) throws Exception {
        statePerson = context.getOperatorStateStore().getListState(new ListStateDescriptor<>(
                "statePerson",
                Long.class));
        stateEventsCountSoFar = context.getOperatorStateStore()
                .getListState(new ListStateDescriptor<>("stateEventsCountSoFar",  Long.class));
        for (Long l : statePerson.get()) {
            time = l;
        }
        if (time == null) {
            time = System.currentTimeMillis();
            System.out.println("PersonSourceFunction:  Initialized time value state");
        } else {
            System.out.println("PersonSourceFunction:  Value state recovered.. time="+time);
        }
        for (Long l : stateEventsCountSoFar.get()) {
            eventsCountSoFar = l;
        }
        if (eventsCountSoFar == null) {
            eventsCountSoFar=0L;
            System.out.println("PersonSourceFunction:  Initialized eventsCountSoFar value state");
        } else {
            System.out.println("PersonSourceFunction:  Value state recovered.. eventsCountSoFar="+eventsCountSoFar);
        }
//        updateRates();
        System.out.println("PersonSourceFunction:  Updated rates, {}" + rates.toString());
    }
}