<script>
export default {
  name: "SimulationProcess",
  props: ["processId"],
  emits: ["close"],
  data() {
    return {
      process: null,
      jobs: null,
      inputs: {},
      loadingJobs: false,
      jobsPerPage: 6,
      currentJobsPageIndex: 0,
    };
  },
  computed: {
    numberOfJobsPages() {
      return Math.ceil((this.jobs?.length || 0) / this.jobsPerPage);
    },
    maxJobsPagesIndex() {
      return this.numberOfJobsPages - 1;
    },
    currentPageJobs() {
      const start = this.currentJobsPageIndex * this.jobsPerPage;
      const end = start + this.jobsPerPage;
      return (this.jobs || []).slice(start, end);
    },
  },
  methods: {
    async fetchProcess(processId) {
      this.process = await fetch(
        `http://localhost:3000/api/processes/${processId}`,
        {
          headers: { "content-type": "application/json" },
        }
      ).then((res) => res.json());
    },
    async fetchJobs(processId) {
      this.loadingJobs = true;
      this.jobs = await fetch(`http://localhost:3000/api/jobs`)
        .then((res) => res.json())
        .then((json) => json.jobs.filter((job) => job.processID === processId));

      this.loadingJobs = false;

      // update jobs list if there are jobs running
      if (
        this.jobs.some((job) => ["accepted", "running"].includes(job.status))
      ) {
        setTimeout(() => this.fetchJobs(processId), 5000);
      }
    },
    async execute(event) {
      event.preventDefault();
      const processId = this.process.id;
      const body = { mode: "async", inputs: this.inputs };
      await fetch(
        `http://localhost:3000/api/processes/${processId}/execution`,
        {
          method: "POST",
          body: JSON.stringify(body),
          headers: { "Content-Type": "application/json" },
        }
      ).then((res) => res.json());
      this.fetchJobs(processId);
    },
  },
  mounted() {
    this.fetchProcess(this.processId);
    this.fetchJobs(this.processId);
  },
};
</script>

<template>
  <div>
    <div class="process-details">
      <div :class="{ 'process-header': true, 'placeholder-glow': !process }">
        <a class="bootstrap-icon" href="#" @click="$emit('close')" title="Back">
          <i class="bi-chevron-left"></i>
        </a>

        <h3 :class="{ placeholder: !process }" :aria-hidden="!process">
          {{ process?.title || "Loading process name" }}
        </h3>
      </div>

      <p v-if="process">{{ process.description }}</p>
      <p v-else class="placeholder-glow" aria-hidden>
        <span class="placeholder col-3" />
        <span class="placeholder col-4" />
        <span class="placeholder col-4" />
        <span class="placeholder col-6" />
        <span class="placeholder col-3" />
      </p>
    </div>

    <template v-if="process">
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
                  {{ new Date(job.job_start_datetime).toLocaleString() }}
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
                  <a v-if="job.status === 'successful'" href="#">
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
          <nav
            v-if="jobs?.length > jobsPerPage"
            aria-label="Jobs navigation example"
          >
            <ul class="pagination pagination-sm">
              <li
                :class="{
                  'page-item': true,
                  disabled: currentJobsPageIndex <= 0,
                }"
              >
                <a
                  class="page-link"
                  @click.prevent="
                    currentJobsPageIndex = Math.max(currentJobsPageIndex - 1, 0)
                  "
                  :tabindex="currentJobsPageIndex <= 0 ? -1 : 0"
                  :aria-disabled="currentJobsPageIndex <= 0"
                  aria-label="Previous"
                >
                  <span aria-hidden="true">&laquo;</span>
                </a>
              </li>

              <li
                v-for="(pageNumber, index) in numberOfJobsPages"
                :key="pageNumber"
                :class="{
                  'page-item': true,
                  active: index === currentJobsPageIndex,
                }"
              >
                <a
                  class="page-link"
                  @click.prevent="currentJobsPageIndex = index"
                >
                  {{ pageNumber }}
                </a>
              </li>

              <li
                :class="{
                  'page-item': true,
                  disabled: currentJobsPageIndex >= numberOfJobsPages,
                }"
              >
                <a
                  class="page-link"
                  @click.prevent="
                    currentJobsPageIndex = Math.min(
                      currentJobsPageIndex + 1,
                      maxJobsPagesIndex
                    )
                  "
                  :tabindex="currentJobsPageIndex >= numberOfJobsPages ? -1 : 0"
                  :aria-disabled="currentJobsPageIndex >= numberOfJobsPages"
                  aria-label="Next"
                >
                  <span aria-hidden="true">&raquo;</span>
                </a>
              </li>
            </ul>
          </nav>

          <div v-if="jobs?.length && loadingJobs" class="loader text-black-50">
            <span class="spinner-border spinner-border-sm"></span>
            Updating Jobs...
          </div>
        </div>
      </section>

      <section v-if="process?.inputs">
        <h4>Execute Job</h4>

        <form class="execution-form">
          <template v-for="(input, key) in process.inputs">
            <label
              :title="input.description"
              :for="`input_${key}`"
              :key="`label_${key}`"
            >
              {{ input.title }}:
            </label>

            <!-- 

          [
            {
              "title": "String",
              "description": "A string parameter",
              "schema": {
                "type": "string", // array | boolean | integer | number | object | string
                "maxLength": 1,
                "minLength": 2,
                "pattern": "",
                "default": "hello"
              },
              "minOccurs": 0,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Boolean",
              "description": "A boolean parameter",
              "schema": {
                "type": "boolean",
                "default": 456
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Number",
              "description": "A number parameter",
              "schema": {
                "type": "number",
                "minimum": 2,
                "maximum": 3,
                "default": 456
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            },
            {
              "title": "Array of numbers",
              "description": "An array parameter",
              "schema": {
                "type": "array",
                "minItems": 0,
                "maxItems": 3,
                "items": {
                  "type": "number"
                }
              },
              "minOccurs": 1,
              "maxOccurs": 1,
              "metadata": {
                "display": "range"
              }
            }
          ]


         -->
            <input
              v-if="input.schema.type === 'string'"
              class="form-control"
              :id="`input_${key}`"
              :name="`input_${key}`"
              type="text"
              v-model="inputs[key]"
              required
              :key="`input_${key}`"
            />
            <input
              v-else
              class="form-control"
              :id="`input_${key}`"
              :name="`input_${key}`"
              type="number"
              min="3"
              v-model.number="inputs[key]"
              required
              :key="`input_${key}`"
            />
          </template>

          <button
            class="btn btn-primary btn-sm"
            type="submit"
            @click="execute"
            :disabled="
              !Object.entries(inputs).filter(([, value]) => Boolean(value))
                .length
            "
          >
            Run job
          </button>
        </form>
      </section>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.process-details {
  position: sticky;
  top: -1.25rem;
  margin: -1.25rem -1.25rem 1rem;
  padding: 1.25rem 1.25rem 0;
  background: white;
}

.process-details::after {
  content: "";
  display: block;
  border-bottom: 1px solid rgba(0, 0, 0, 0.25);
}

.process-header {
  display: flex;
  align-items: center;
  column-gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.process-header > * {
  margin: 0;
}

section:not(:last-child) {
  margin-bottom: 2rem;
}

.execution-form {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem;
  align-items: center;
}

.execution-form label {
  text-align: right;
}

.execution-form button {
  grid-column: 2;
}

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
