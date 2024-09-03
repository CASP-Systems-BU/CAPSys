package org.apache.flink.runtime.resourcemanager.slotmanager;

import org.apache.flink.runtime.clusterframework.types.ResourceProfile;
import org.apache.flink.runtime.instance.InstanceID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collection;
import java.util.Optional;
import java.util.function.Function;

public enum LocationSlotMatchingStrategy implements SlotMatchingStrategy {
    INSTANCE;

    @Override
    public <T extends TaskManagerSlotInformation> Optional<T> findMatchingSlot(
            ResourceProfile requestedProfile,
            Collection<T> freeSlots,
            Function<InstanceID, Integer> numberRegisteredSlotsLookup) {

        Logger LOG = LoggerFactory.getLogger(LocationSlotMatchingStrategy.class);
        LOG.info(
                "mylog    LocationSlotMatchingStrategy Location slot matching at Slot Manager ============================= {} {}",
                freeSlots.size(),
                requestedProfile);

        //        freeSlots.stream().forEach(s -> LOG.info("Slot ID: {}",s.getSlotId().toString()));

        return freeSlots.stream()
                .filter(
                        slot ->
                                slot.getSlotId()
                                        .toString()
                                        .contains(requestedProfile.getPreferredLocation()))
                .findAny();
    }
}
