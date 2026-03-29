"use client";

import { useState } from "react";
import { create } from "zustand";

interface ScenarioState {
  selectedScenarioId: string | null;
  scenarioParams: Record<string, unknown>;
  setSelectedScenario: (id: string | null) => void;
  setScenarioParams: (params: Record<string, unknown>) => void;
  reset: () => void;
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  selectedScenarioId: null,
  scenarioParams: {},
  setSelectedScenario: (id) => set({ selectedScenarioId: id }),
  setScenarioParams: (params) =>
    set((state) => ({ scenarioParams: { ...state.scenarioParams, ...params } })),
  reset: () => set({ selectedScenarioId: null, scenarioParams: {} }),
}));
