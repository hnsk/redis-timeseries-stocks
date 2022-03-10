<template>
    <div>
        <div>
            <q-list bordered padding>
            <q-item v-for="symbol of searchResults" :key="symbol.id" clickable>
                <q-item-section @click="selectSymbol(symbol.symbol, symbol.exchange)">
                    <q-item-label overline>{{ symbol.symbol }} ({{ symbol.exchange }})</q-item-label>
                    <q-item-label caption><span v-html="symbol.company_name" /></q-item-label>
                </q-item-section>
            </q-item>
            </q-list>
            </div>
    </div>
</template>

<script setup>
import { ref, watch } from "vue"
import { api } from "boot/axios"

const props = defineProps({
  searchInput: String
})

const searchResults = ref("")

function searchSymbols(query) {
    let searchStr = `${query}* | @symbol:{${query}}`
    api.post('api/search', {
        query: searchStr
    })
    .then((response) => {
        console.log(response.data)
        searchResults.value = response.data.results
    })
}

watch(props, (newValue) => {
    if (newValue['searchInput']) {
        searchSymbols(newValue.searchInput)
    }
})

const emit = defineEmits(["symbolSelected"])

function selectSymbol(symbol, exchange) {
    //console.log(exchange)
    emit('symbolSelected', {
        symbol: symbol,
        exchange: exchange
    })
    //searchInput.value = newInput
}

</script>