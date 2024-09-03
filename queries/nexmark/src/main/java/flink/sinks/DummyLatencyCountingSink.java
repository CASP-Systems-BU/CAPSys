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

package flink.sinks;

import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.streaming.api.operators.StreamSink;
import org.apache.flink.streaming.runtime.streamrecord.LatencyMarker;

import org.slf4j.Logger;


/**
 * A Sink that drops all data and periodically emits latency measurements
 */
public class DummyLatencyCountingSink<T> extends StreamSink<T> {

    private final Logger LOG;
    public String markerID;

    public DummyLatencyCountingSink(Logger log) {
        super(new SinkFunction() {

            @Override
            public void invoke(Object value, Context ctx) {
            }
        });
        LOG = log;
    }

    @Override
    public void processLatencyMarker(LatencyMarker marker) {
        long currentTime=System.currentTimeMillis();
        long lMarkedTime=marker.getMarkedTime();
        LOG.warn("%{}%{}%{}%{}%{}%{}%{}%{}%{}%{}", "latency",
                currentTime-lMarkedTime,
                currentTime,
                lMarkedTime,
                marker.getSubtaskIndex(),
                getRuntimeContext().getIndexOfThisSubtask(),
                marker.getOperatorId()+"_"+marker.getSubtaskIndex(),
                "Sink",
                "processLatencyMarker",
                "latencyFromSink_"+markerID
        );
    }
}