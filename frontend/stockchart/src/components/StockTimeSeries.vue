<template>
    <div>
        <div style="width: 100%">
            <div
                v-for="(chart, idx) in charts"
                :key="idx"
                class="row"
            >   
                <div style="width: 90%">
                    <LineChart 
                        :chartData="chart.chartData"
                        :options="chart.chartOptions"
                    />
                </div>
                <div class="row justify-center items-center">
                    <q-btn
                        @click="charts.splice(idx, 1)"
                        class="q-ma-sm"
                        icon="close"
                        flat
                    />
                </div>
                <q-space />
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, watch } from "vue"
import { api } from "boot/axios"

import { LineChart } from 'vue-chart-3';
import { Chart, registerables } from "chart.js";
import 'chartjs-adapter-moment';

Chart.register(...registerables);

const props = defineProps({
  searchInput: String,
  searchSymbol: Object
})

const chartOptions = {
    scales: {
        xAxis: {
            type: 'time',
        },
        prices: {
            title: {
                display: true,
                text: "Price ($)"
            },
            type: 'linear',
            display: true,
            position: 'left'
        },
        volume: {
            title: {
                display: true,
                text: "Volume"
            },
            type: 'linear',
            display: true,
            position: 'right'
        }
    },
    interaction: {
        mode: 'index'
    },
    elements: {
        point: {
            radius: 0
        }
    },
    plugins: {
        title: {
            display: true,
            text: "Stock"
        }
    }

}

let charts = ref([])

const chartColors = {
    volume: "#7E7E7E",
    low: "#FF0000",
    high: "#00FF00",
    open: "#8300FF",
    close: "#FF7400"

}

function getTimeSeries(symbol, exchange) {
    api.post('api/timeseries/mrange', {
        from_time: "-",
        to_time: "+",
        filters: [
            `exchange=${exchange}`,
            `symbol=${symbol}`
        ]
    })
    .then((response) => {
        console.log(response.data)
        if (response.data.length > 0) {
            let newChart = {
                chartData: {
                    datasets: []
                },
                chartOptions: {...chartOptions}
            }

            //let new_series = []
            for (let serie of response.data) {
                if (serie.name === "volume") {
                    serie.type = "bar"
                    serie.yAxisID = "volume"
                }
                else {
                    serie.type = "line"
                    serie.yAxisID = "prices"

                }
                serie.label = serie.name
                serie.borderColor = chartColors[serie.label]
                serie.borderWidth = 2
                newChart.chartData.datasets.push(serie)
            }
            newChart.chartOptions.plugins.title.text = `${response.data[0].exchange.toUpperCase()}:${response.data[0].symbol} - ${response.data[0].company_name}`
            charts.value.push(newChart)
            /*
            chartData.value.datasets.splice(
                0,
                chartData.value.datasets.length,
                ...new_series
            )
            */
        }
    })
}

watch(props, (newValue) => {
    console.log(newValue)
    if (newValue['searchSymbol']) {
        getTimeSeries(newValue['searchSymbol'].symbol, newValue['searchSymbol'].exchange)
        console.log(newValue['searchSymbol'])
    }
    //options.value.title.text = "MOI"
    //getTimeSeries(props.searchInput.toUpperCase())
})
</script>