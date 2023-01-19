<script>
import Chart from "chart.js";
import { and, equalTo } from "ol/format/filter";
import WFS from "ol/format/WFS";

export default {
    name: "SimulationProcessJob",
    props: ["jobId", "processId"],
    emits: ["close"],
    data() {
        return {
            job: null,
            graphData: null,
            chart: null,
            chartType: "line",
            // prettier-ignore
            apiUrl: Config.simulationApiUrl,
            layer: null,
            displayMapFilters: [],
            mapFilters: [],
        };
    },
    watch: {
        chartType() {
            this.renderChart();
        },
        mapFilters: {
            handler: function (newVal, oldVal) {
                if (!oldVal.length) {
                    return;
                }

                this.updateLayer(newVal);
            },
            deep: true,
        },
    },
    methods: {
        async fetchJob(jobId) {
            this.job = await fetch(`${this.apiUrl}/jobs/${jobId}`, {
                headers: { "content-type": "application/json" },
            }).then((res) => res.json());
        },

        getChartData() {
            const result = {};

            for (const data of this.graphData) {
                // Count agents per Stadtviertel
                const id = data.AgentID.split("-")[0];
                result[id] = result[id] ? result[id] + 1 : 1;
            }

            return {
                labels: Object.keys(result),
                data: Object.values(result),
            };
        },

        renderChart() {
            const barChartData = this.getChartData();
            const data = {
                labels: barChartData.labels,
                datasets: [
                    {
                        data: barChartData.data,
                        backgroundColor: "cornflowerblue",
                    },
                ],
            };

            // Update or remove previous chart
            if (this.chart && this.chart.config.type === this.chartType) {
                this.chart.data.datasets[0].data = data.datasets[0].data;
                this.chart.update();
                return;
            } else {
                this.chart?.destroy();
            }

            // Render the new chart
            const context = this.$refs.chart.getContext("2d");
            this.chart = new Chart(context, {
                type: this.chartType,
                data,
                options: {
                    legend: {
                        display: false,
                    },
                },
            });
        },

        createLayer() {
            if (!this.layer) {
                this.layer = Radio.request(
                    "ModelList",
                    "getModelByAttributes",
                    {
                        isSimulationLayer: true,
                        modelId: this.processId,
                    }
                );
            }
        },

        async updateLayer() {
            const urlParams = new URLSearchParams();
            urlParams.append("service", "wfs");
            urlParams.append("version", "1.0.0");
            urlParams.append("request", "getFeature");
            urlParams.append("outputFormat", "application/json");
            urlParams.append("typeName", "CUT:results_XS");

            const filters = this.mapFilters.filter((mf) => mf.active);

            if (filters.length) {
                const olFilter =
                    filters.length < 2
                        ? equalTo(filters[0].key, filters[0].value)
                        : and(
                              ...filters.map((mf) => equalTo(mf.key, mf.value))
                          );

                const requestOptions = {
                    featureTypes: ["CUT:results_XS"],
                    filter: olFilter,
                };
                const getFeatureRequest = new WFS().writeGetFeature(
                    requestOptions
                );
                const filterString = new XMLSerializer().serializeToString(
                    getFeatureRequest.querySelector("Filter")
                );
                urlParams.append("filter", filterString);
            }

            const geoserverUrl = Config.simulationGeoserverWorkspaceUrl;
            const url = `${geoserverUrl}?${urlParams.toString()}`;

            const source = this.layer.layer.getSource();
            source.setUrl(url);
            source.refresh();

            // update charts
            source.once("featuresloadend", () => {
                this.graphData = source.getFeatures().map((feature) => {
                    const properties = { ...feature.getProperties() };
                    delete properties.geometry;
                    return properties;
                });
                this.renderChart();
            });
        },

        initMapFilters() {
            this.mapFilters = [
                { key: "Step", value: 0, active: true },
                { key: "iteration", value: 0, active: false },
                {
                    key: "AgentID",
                    value: "",
                    active: false,
                    options: ["Bahrenfeld-1", "Rotherbaum-0"],
                },
            ];
            this.displayMapFilters = structuredClone(this.mapFilters);
        },

        setMapFilter(key, value, active) {
            const filter = this.displayMapFilters.find((mf) => mf.key === key);
            filter.value = value;
            filter.active = active;
        },

        commitMapFilters() {
            this.mapFilters = structuredClone(this.displayMapFilters);
        },
    },
    async mounted() {
        await this.fetchJob(this.jobId);
        this.initMapFilters();
        this.createLayer();
        this.updateLayer();
    },

    beforeDestroy() {
        this.layer?.layer.getSource().clear();
    },
};
</script>

<template>
    <div>
        <div class="job-details">
            <div :class="{ 'job-header': true, 'placeholder-glow': !job }">
                <a
                    class="bootstrap-icon"
                    href="#"
                    @click="$emit('close')"
                    title="Back"
                >
                    <i class="bi-chevron-left"></i>
                </a>

                <h3 :class="{ placeholder: !job }" :aria-hidden="!job">
                    {{
                        job
                            ? `Job ${new Date(
                                  job.job_start_datetime
                              ).toLocaleString()}`
                            : "Loading job name"
                    }}
                </h3>
            </div>

            <div v-if="job" class="job-data">
                <div>
                    Status:
                    <span
                        :class="{
                            status: true,
                            'text-bg-info':
                                job.status !== 'successful' &&
                                job.status !== 'failed',
                            'text-bg-success': job.status === 'successful',
                            'text-bg-danger': job.status === 'failed',
                        }"
                    >
                        {{ job.status }}
                    </span>
                </div>
                <div>
                    Started:
                    {{ new Date(job.job_start_datetime).toLocaleString() }}
                </div>
                <div>
                    Ended: {{ new Date(job.job_end_datetime).toLocaleString() }}
                </div>
            </div>
            <p v-else class="placeholder-glow" aria-hidden>
                <span class="placeholder col-3" />
                <span class="placeholder col-4" />
                <span class="placeholder col-4" />
                <span class="placeholder col-6" />
                <span class="placeholder col-3" />
            </p>
        </div>

        <div class="job-filter" v-if="job">
            <h4>Property Filter</h4>
            <ul>
                <li v-for="filter in displayMapFilters" :key="filter.key">
                    <label>{{ filter.key }}</label>
                    <input
                        type="checkbox"
                        :checked="filter.active"
                        @change="
                            (event) => {
                                setMapFilter(
                                    filter.key,
                                    filter.value,
                                    event.target.checked
                                );
                                commitMapFilters();
                            }
                        "
                    />
                    <input
                        v-if="typeof filter.value === 'number'"
                        type="range"
                        min="0"
                        max="10"
                        step="1"
                        :value="filter.value"
                        :disabled="!filter.active"
                        @input="
                            (event) =>
                                setMapFilter(
                                    filter.key,
                                    Number(event.target.value),
                                    filter.active
                                )
                        "
                        @change="commitMapFilters()"
                    />

                    <select
                        v-else
                        :value="filter.value"
                        :disabled="!filter.active"
                        @change="
                            (event) => {
                                setMapFilter(
                                    filter.key,
                                    event.target.value,
                                    filter.active
                                );
                                commitMapFilters();
                            }
                        "
                    >
                        <option
                            v-for="option in filter.options"
                            :value="option"
                        >
                            {{ option }}
                        </option>
                    </select>

                    <span v-if="typeof filter.value === 'number'">{{
                        filter.value
                    }}</span>
                </li>
            </ul>
        </div>

        <div class="job-graphs" v-if="job">
            <h4>Charts</h4>
            <ul class="nav nav-pills nav-fill">
                <li
                    class="nav-item"
                    v-for="type in ['line', 'radar', 'bar']"
                    :key="type"
                >
                    <a
                        :class="{
                            'nav-link': true,
                            active: chartType === type,
                        }"
                        :aria-current="chartType === type ? 'page' : false"
                        href="#"
                        @click.prevent="chartType = type"
                    >
                        {{ type.charAt(0).toUpperCase() + type.slice(1) }} Chart
                    </a>
                </li>
            </ul>

            <canvas ref="chart" width="400" height="300"></canvas>
        </div>
    </div>
</template>

<style lang="scss" scoped>
.job-details {
    position: sticky;
    top: -1.25rem;
    margin: -1.25rem -1.25rem 1rem;
    padding: 1.25rem 1.25rem 0;
    background: white;
}

.job-details::after {
    content: "";
    display: block;
    border-bottom: 1px solid rgba(0, 0, 0, 0.25);
}

.job-header {
    display: flex;
    align-items: center;
    column-gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.job-header > * {
    margin: 0;
}

.job-data {
    display: grid;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
}

.status {
    padding: 0.1em 0.5em;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.job-graphs {
    display: grid;
    gap: 1rem;
}

.job-graphs canvas {
    margin-top: 2rem;
}

.job-filter {
    padding: 1em 0;
}

.job-filter ul {
    padding: 0;
}

.job-filter li {
    display: grid;
    padding: 1em 0;
    grid-template-columns: 5em auto 1fr minmax(2em, auto);
    gap: 1em;
    align-items: center;
}

.job-filter li label {
    font-weight: bold;
}

.job-filter li select {
    padding: 0.25em 0.5em;
}
</style>

