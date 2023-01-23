<script>
import SimulationPagination from "./SimulationPagination.vue";

export default {
  name: "SimulationProcessJobsTable",
  props: ["processId", "jobs", "loadingJobs"],
  emits: ["selected"],
  components: { SimulationPagination },
  data() {
    return {
      jobsPerPage: 6,
      currentJobsPageIndex: 0,
    };
  },
  computed: {
    numberOfJobsPages() {
      return Math.ceil((this.jobs?.length || 0) / this.jobsPerPage);
    },
    currentPageJobs() {
      const start = this.currentJobsPageIndex * this.jobsPerPage;
      const end = start + this.jobsPerPage;
      return (this.jobs || []).slice(start, end);
    },
  },
};
</script>

<template v-if="processId">
  <section>
    <h4>Jobs</h4>

    <table class="table">
      <thead>
        <tr>
          <th scope="col" class="col-4">Start Time</th>
          <th scope="col" class="col-3">Status</th>
          <th scope="col">Result</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="jobs?.length">
          <tr v-for="job in currentPageJobs" :key="job.jobID">
            <td class="time">
              {{ new Date(job.started).toLocaleString() }}
            </td>
            <td>
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
            </td>
            <td>
              <span v-if="job.status === 'failed'" class="text-danger">
                {{ job.message }}
              </span>
              <a
                v-if="job.status === 'successful'"
                href="#"
                @click="$emit('selected', job.jobID)"
              >
                View results
              </a>
            </td>
          </tr>
        </template>

        <tr v-else-if="loadingJobs" class="placeholder-glow" aria-hidden>
          <td><span class="placeholder d-block" /></td>
          <td><span class="placeholder d-block" /></td>
          <td><span class="placeholder d-block" /></td>
        </tr>

        <tr v-else>
          <td colspan="3" class="text-black-50">No jobs yet</td>
        </tr>
      </tbody>
    </table>

    <div class="jobs-table-footer">
      <SimulationPagination
        v-if="jobs?.length > jobsPerPage"
        :itemsPerPage="jobsPerPage"
        :currentPageIndex="currentJobsPageIndex"
        :numberOfPages="numberOfJobsPages"
        @pageChange="currentJobsPageIndex = $event"
      />

      <div v-if="jobs?.length && loadingJobs" class="loader text-black-50">
        <span class="spinner-border spinner-border-sm"></span>
        Updating Jobs...
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.time {
  white-space: nowrap;
}

.status {
  padding: 0.1em 0.5em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.jobs-table-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.pagination {
  margin: 0;
}

.loader {
  display: flex;
  align-items: center;
  column-gap: 0.5em;
  white-space: nowrap;
}
</style>
