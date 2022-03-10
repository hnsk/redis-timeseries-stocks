<template>
    <div>
        <div>
            <q-input color="purple-12" v-model="searchInput" label="Search stocks" @update:model-value="readSearchInput">
                <template v-slot:prepend>
                <q-icon class="q-ml-sm" name="search" />
                </template>
            </q-input>
        </div>
        <StockSelector
            @symbolSelected="symbolSelected"
            :searchInput="searchInput" />
    </div>
</template>

<script setup>
import StockSelector from "../components/StockSelector.vue"
import { ref } from "vue"
import { api } from "axios"

const searchInput = ref("")
const emit = defineEmits([
    "searchInputChanged",
    "symbolSelected"
])

function readSearchInput(newInput) {
    //emit('searchInputChanged', newInput)
    searchInput.value = newInput
}

function symbolSelected(symbol) {
    emit('symbolSelected', symbol)
    //console.log(exchange)
} 

</script>