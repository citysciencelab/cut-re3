<script>
import Chart from "chart.js";

export default {
  name: "SimulationProcessJob",
  props: ["jobId"],
  emits: ["close"],
  data() {
    return {
      job: null,
      jobDetails: null,
      chart: null,
      chartType: "line",
      // prettier-ignore
      colors: ["red", "pink", "magenta", "purple", "lavender", "blue", "teal", "turquoise", "green", "olive", "greenyellow", "yellow", "orange", "brown"],
    };
  },
  watch: {
    chartType() {
      this.renderChart();
    },
  },
  methods: {
    async fetchJob(jobId) {
      this.job = await fetch(`http://localhost:3000/api/jobs/${jobId}`, {
        headers: { "content-type": "application/json" },
      }).then((res) => res.json());

      const detailsLink = this.job.links.find(
        (link) => link.type === "application/json"
      );

      if (detailsLink) {
        this.fetchJobDetails(detailsLink.href);
      }
    },
    async fetchJobDetails(url) {
      const response = await fetch(url, {
        headers: { "content-type": "application/json" },
      }).then((res) => res.json());
      const jobGeoJSON = JSON.parse(response.geojson);

      this.jobDetails = jobGeoJSON?.features.map(
        ({ properties }) => properties
      );

      this.renderChart();
    },
    renderChart() {
      const labels = new Set();
      const speedPerAgent = {};

      for (const data of this.jobDetails) {
        if (this.chartType === "bar") {
          // Get the average speed of the agents
          labels.add(data.AgentID);

          const agentSpeed = speedPerAgent[data.AgentID] || [];
          speedPerAgent[data.AgentID] = [...agentSpeed, data.Geschwindigkeit];
        } else {
          // Get the speed of agents per timestep
          labels.add(data.Step);

          const agentSpeed = speedPerAgent[data.AgentID] || [];
          agentSpeed[data.Step] = data.Geschwindigkeit;
          speedPerAgent[data.AgentID] = agentSpeed;
        }
      }

      const datasets =
        this.chartType === "bar"
          ? [
              {
                label: "Average Agent Speed",
                data: Object.values(speedPerAgent).map(
                  (data) =>
                    data.reduce((sum, value) => sum + value, 0) / data.length
                ),
                backgroundColor: this.colors[0],
              },
            ]
          : Object.entries(speedPerAgent).map(([label, data], index) => ({
              label,
              data,
              fill: false,
              borderColor: this.colors[index % this.colors.length],
            }));

      // Remove previous chart
      if (this.chart) {
        this.chart.destroy();
      }

      // Render the new chart
      const context = this.$refs.chart.getContext("2d");
      this.chart = new Chart(context, {
        type: this.chartType,
        data: {
          labels: [...labels],
          datasets,
        },
        options: {
          legend: {
            display: false,
          },
        },
      });
    },
  },
  mounted() {
    this.fetchJob(this.jobId);
  },
};
</script>

<template>
  <div>
    <div class="job-details">
      <div :class="{ 'job-header': true, 'placeholder-glow': !job }">
        <a class="bootstrap-icon" href="#" @click="$emit('close')" title="Back">
          <i class="bi-chevron-left"></i>
        </a>

        <h3 :class="{ placeholder: !job }" :aria-hidden="!job">
          {{
            job
              ? `Job ${new Date(job.job_start_datetime).toLocaleString()}`
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
                job.status !== 'successful' && job.status !== 'failed',
              'text-bg-success': job.status === 'successful',
              'text-bg-danger': job.status === 'failed',
            }"
          >
            {{ job.status }}
          </span>
        </div>
        <div>
          Started: {{ new Date(job.job_start_datetime).toLocaleString() }}
        </div>
        <div>Ended: {{ new Date(job.job_end_datetime).toLocaleString() }}</div>
      </div>
      <p v-else class="placeholder-glow" aria-hidden>
        <span class="placeholder col-3" />
        <span class="placeholder col-4" />
        <span class="placeholder col-4" />
        <span class="placeholder col-6" />
        <span class="placeholder col-3" />
      </p>
    </div>

    <div class="job-content" v-if="job">
      <ul class="nav nav-pills nav-fill">
        <li
          class="nav-item"
          v-for="type in ['line', 'radar', 'bar']"
          :key="type"
        >
          <a
            :class="{ 'nav-link': true, active: chartType === type }"
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

.job-content {
  display: grid;
  gap: 2rem;
}
</style>
