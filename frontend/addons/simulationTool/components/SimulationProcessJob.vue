<script>
export default {
  name: "SimulationProcessJob",
  props: ["jobId"],
  emits: ["close"],
  data() {
    return {
      job: null,
      jobDetails: null,
    };
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
