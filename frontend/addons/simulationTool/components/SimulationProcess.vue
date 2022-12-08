<script>
export default {
  name: "SimulationProcess",
  props: ["processId"],
  emits: ["close"],
  data() {
    return { process: null, jobs: null };
  },
  methods: {
    async fetchProcess(processId) {
      this.process = await fetch(
        `http://localhost:5001/processes/${processId}`,
        {
          headers: { "content-type": "application/json" },
        }
      ).then((res) => res.json());
    },
    async fetchJobs(processId) {
      this.jobs = await fetch(
        `http://localhost:5001/jobs?processID=${processId}`
      ).then((res) => res.json());
    },
  },
  mounted() {
    this.fetchProcess(this.processId);
    this.fetchJobs(this.processId);
  },
};
</script>

<template>
  <div v-if="process">
    <h1>{{ process.title }}</h1>

    <a href="#" @click="$emit('close')">Back</a>

    <p>{{ process.description }}</p>

    <div v-if="jobs">
      <pre>{{ JSON.stringify(jobs, null, 2) }}</pre>
    </div>

    <pre>{{ JSON.stringify(process, null, 2) }}</pre>
  </div>

  <div v-else>Loading...</div>
</template>

<style lang="scss" scoped></style>
