const actions = {
  /**
   * Increases the count state.
   *
   * @param {Object} context actions context object.
   * @returns {void}
   */
  async fetchProcesses({ state, commit }) {
    const response = await fetch("http://localhost:3000/api/processes", {
      headers: { "content-type": "application/json" },
    }).then((res) => res.json());

    commit("setProcesses", response.processes);
  },

  /**
   * Increases the count state.
   *
   * @param {Object} context actions context object.
   * @returns {void}
   */
  async fetchProcess({ state, commit }, processIndex) {
    const process = state.processes[processIndex];
    const response = await fetch(
      `http://localhost:3000/api/processes/${process.id}`,
      {
        headers: { "content-type": "application/json" },
      }
    ).then((res) => res.json());

    commit("setProcess", response);
  },
};

export default actions;
