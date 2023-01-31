<script>
import SimulationPagination from "./SimulationPagination.vue";
import SimulationProcessJobRow from "./SimulationProcessJobRow.vue";

export default {
    name: "SimulationProcessJobsTable",
    props: ["process", "jobs", "loadingJobs"],
    emits: ["selected"],
    components: { SimulationPagination, SimulationProcessJobRow },
    data() {
        return {
            jobsPerPage: 6,
            currentJobsPageIndex: 0,
            expandedParameterJobIds: [],
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
    methods: {
        displayParameters(parameters) {
            const params = { ...parameters };
            delete params.mode;

            const entries = Object.entries(params).map(([key, value]) => [
                this.process.inputs[key].title,
                value,
            ]);

            return Object.fromEntries(entries);
        },
        areParametersExpanded(jobId) {
            return Boolean(this.expandedParameterJobIds.includes(jobId));
        },
        toggleExpandParameters(jobId) {
            if (this.areParametersExpanded(jobId)) {
                this.expandedParameterJobIds =
                    this.expandedParameterJobIds.filter((id) => id !== jobId);
            } else {
                this.expandedParameterJobIds.push(jobId);
            }
        },
    },
};
</script>

<template v-if="process">
    <section>
        <h4>Jobs</h4>
        <div v-if="jobs?.length" class="job-grid">
            <div class="grid-header">Start Time</div>
            <div class="grid-header">Status</div>
            <div class="grid-header">Parameters</div>
            <div class="grid-header">Result</div>

            <template v-for="job in currentPageJobs">
                <div class="job-date">
                    {{ new Date(job.started).toLocaleString() }}
                </div>
                <div>
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
                <div class="job-parameter-button">
                    <!-- <a href="#" @click="toggleExpandParameters(job.jobID)">{{
                        areParametersExpanded(job.jobID) ? "Hide" : "Show"
                    }}</a> -->
                    <button
                        class="btn btn-secondary btn-sm"
                        @click="toggleExpandParameters(job.jobID)"
                    >
                        {{ areParametersExpanded(job.jobID) ? "Hide" : "Show" }}
                    </button>
                </div>
                <div>
                    <span v-if="job.status === 'failed'" class="text-danger">
                        n/a
                    </span>
                    <a
                        v-if="job.status === 'successful'"
                        href="#"
                        @click="$emit('selected', job.jobID)"
                    >
                        View
                    </a>
                </div>

                <div
                    v-if="areParametersExpanded(job.jobID)"
                    class="job-parameter"
                >
                    <table>
                        <tr
                            v-for="(value, key) in displayParameters(
                                job.parameters.inputs
                            )"
                        >
                            <th>{{ key }}:{{ " " }}</th>
                            <td>
                                {{ value }}
                            </td>
                        </tr>
                    </table>
                </div>
            </template>
        </div>
        <div class="jobs-table-footer">
            <SimulationPagination
                v-if="jobs?.length > jobsPerPage"
                :itemsPerPage="jobsPerPage"
                :currentPageIndex="currentJobsPageIndex"
                :numberOfPages="numberOfJobsPages"
                @pageChange="currentJobsPageIndex = $event"
            />

            <div
                v-if="jobs?.length && loadingJobs"
                class="loader text-black-50"
            >
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
    margin-top: 1em;
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

.job-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    grid-gap: 1em;

    .grid-header {
        white-space: nowrap;
        color: #666;
        font-weight: bold;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .job-date {
        white-space: nowrap;
    }

    .job-parameter-button button {
        padding: 0.1em 0.5em;
        min-width: 4em;
    }

    .job-parameter {
        grid-column: 1 / -1;
        padding-left: 1em;
        border-left: 4px solid rgba(0, 0, 0, 0.1);

        table {
            line-height: 1.4;
        }

        td {
            padding-left: 1em;
        }
    }
}
</style>

