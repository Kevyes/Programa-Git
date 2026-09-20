package com.kevyes.calzadoapp.domain;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

public class InventoryRulesTest {
    @Test
    public void movesStockToTestCorrectly() {
        assertEquals(5, InventoryRules.availableAfterTemporaryExit(8, 3));
        assertEquals(3, InventoryRules.testAfterTemporaryExit(0, 3));
    }

    @Test
    public void returnsStockCorrectly() {
        assertEquals(11, InventoryRules.availableAfterReturn(8, 3));
        assertEquals(0, InventoryRules.testAfterReturn(3, 3));
    }

    @Test
    public void rejectsInsufficientAvailableStock() {
        assertThrows(IllegalStateException.class,
                () -> InventoryRules.availableAfterTemporaryExit(2, 3));
    }

    @Test
    public void rejectsInsufficientTestStock() {
        assertThrows(IllegalStateException.class,
                () -> InventoryRules.testAfterReturn(1, 2));
    }

    @Test
    public void calculatesSaleTotal() {
        assertEquals(1050000.0, InventoryRules.total(350000, 3), 0.001);
    }
}
