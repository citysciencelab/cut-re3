<script>
const API_URL = "http://localhost:3000/api";

export default {
  name: "SimulationVisualizer",
  props: ["jobId"],
  emits: ["close", "addLayer"],
  data() {
    return { job: null, loadingJob: false };
  },
  methods: {
    async fetchJob(jobId) {
      this.loadingJob = true;
      this.job = await fetch(`${API_URL}/jobs/${jobId}`).then((res) =>
        res.json()
      );

      this.loadingJob = false;
    },
  },
  mounted() {
    this.fetchJob(this.jobId);
  },
};
</script>

<template>
  <div v-if="job">
    <a href="#" @click="$emit('close')">Back</a>
    <h1>{{ job.jobID }}</h1>

    <p>{{ job.job_start_datetime }}</p>

    <button @click="$emit('addLayer')">Add Layer</button>

    <pre>{{ JSON.stringify(job, null, 2) }}</pre>
  </div>

  <div v-else>Loading...</div>
</template>

<style lang="scss" scoped></style>
