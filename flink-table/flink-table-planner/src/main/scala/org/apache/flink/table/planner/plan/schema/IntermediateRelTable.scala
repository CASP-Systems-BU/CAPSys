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
package org.apache.flink.table.planner.plan.schema

import org.apache.flink.annotation.Internal
import org.apache.flink.table.planner.plan.`trait`.{ModifyKindSet, UpdateKind}
import org.apache.flink.table.planner.plan.stats.FlinkStatistic

import org.apache.calcite.rel.RelNode
import org.apache.calcite.util.ImmutableBitSet

import java.util
import java.util.{List => JList, Set}

/**
 * An intermediate Table to wrap a optimized RelNode inside. The input data of this Table is
 * generated by the underlying optimized RelNode.
 *
 * @param relNode
 *   underlying optimized RelNode
 * @param modifyKindSet
 *   the modify operations kind sets will be produced by the underlying relNode
 * @param isUpdateBeforeRequired
 *   true relNode is required to send UPDATE_BEFORE message for update changes by some parent
 *   blocks.
 * @param statistic
 *   statistics of current Table
 */
@Internal
class IntermediateRelTable(
    names: JList[String],
    val relNode: RelNode,
    val modifyKindSet: ModifyKindSet,
    val isUpdateBeforeRequired: Boolean,
    val upsertKeys: util.Set[ImmutableBitSet],
    statistic: FlinkStatistic = FlinkStatistic.UNKNOWN)
  extends FlinkPreparingTableBase(null, relNode.getRowType, names, statistic) {

  def this(names: JList[String], relNode: RelNode) {
    this(names, relNode, ModifyKindSet.INSERT_ONLY, false, new util.HashSet[ImmutableBitSet]())
  }
}