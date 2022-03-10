<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> Stock charts </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <StockBar
        @searchInputChanged="searchInputChanged"
        @symbolSelected="symbolSelected"
      />
    </q-drawer>

    <q-page-container>
      <router-view
        :searchInput="searchInput"
        :searchSymbol="searchSymbol"
      />
    </q-page-container>
  </q-layout>
</template>

<script setup>

import { ref } from "vue";

import StockBar from "../components/StockBar.vue"
const leftDrawerOpen = ref(false);
const searchInput = ref("")
const searchSymbol = ref({})

function toggleLeftDrawer() { 
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function searchInputChanged(newInput) {
  searchInput.value = newInput
}

function symbolSelected(symbol) {
  searchSymbol.value = symbol  
}

</script>
