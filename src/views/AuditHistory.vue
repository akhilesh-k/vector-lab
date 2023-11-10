<script setup>
import { ref, onMounted } from "vue";
import DatePicker from "vue3-datepicker";

const startDate = ref(null);
const endDate = ref(null);

const defaultStartDate = new Date();
defaultStartDate.setDate(defaultStartDate.getDate() - 15);
startDate.value = defaultStartDate;
endDate.value = new Date();

const selectedUser = ref(localStorage.getItem("auditorEmail") || "");
const auditedTerms = ref([]);
const auditors = ref([]);
const topRelevantLexicalSearchTerms = ref([]);
const topRelevantHybridSearchTerms = ref([]);
const applyDateFilter = () => {
  // implementation to be done
};

const topIrrelevantLexicalSearchTerms = ref([]);
const topIrrelevantHybridSearchTerms = ref([]);

const convertEmailToName = (email) => {
  const parts = email.split("@")[0].split(".");
  return parts
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};
const apiUrl = "http://xsearch-solr-vector-2.qa2-sg.cld:5000";

const filterSearchTermsByUser = async () => {
  try {
    if (selectedUser.value) {
      const response = await fetch(
        `${apiUrl}/fetch-audited-terms?auditor=${selectedUser.value.auditor}`
      );

      if (response.ok) {
        const data = await response.json();
        auditedTerms.value = data.audited_terms;
      } else {
        auditedTerms.value = [];
      }
    } else {
      auditedTerms.value = [];
    }
  } catch (error) {
    console.error("Error filtering search terms by user:", error);
    auditedTerms.value = [];
  }
};

onMounted(async () => {
  try {
    const auditorsResponse = await fetch(apiUrl + "/fetch-auditors");
    const auditorsData = await auditorsResponse.json();
    auditors.value = auditorsData.auditors;

    const searchTermsResponse = await fetch(apiUrl + "/fetch-top-search-terms");
    const searchTermsData = await searchTermsResponse.json();
    topRelevantLexicalSearchTerms.value =
      searchTermsData.topRelevantLexicalSearchTerms;
    topRelevantHybridSearchTerms.value =
      searchTermsData.topRelevantHybridSearchTerms;
    topIrrelevantLexicalSearchTerms.value =
      searchTermsData.topIrrelevantLexicalSearchTerms;
    topIrrelevantHybridSearchTerms.value =
      searchTermsData.topIrrelevantHybridSearchTerms;
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
</script>

<template>
  <main class="container">
    <section class="header">
      <h3>Audit Reports and History</h3>
      <div class="filters">
        <h4>Filter by Date</h4>
        <div class="date-picker">
          <label for="startDate">Start Date:</label>
          <DatePicker v-model="startDate" type="date" id="startDate" />
          <label for="endDate">End Date:</label>
          <DatePicker
            :upperLimit="new Date()"
            v-model="endDate"
            type="date"
            id="endDate"
          />
          <button @click="applyDateFilter">Apply</button>
        </div>
      </div>
    </section>

    <section class="auditors">
      <h4>Auditors and Audit Count</h4>
      <table class="auditor-table">
        <thead>
          <tr>
            <th>Auditor</th>
            <th>Audit Count</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="auditor in auditors" :key="auditor.auditor">
            <td>{{ convertEmailToName(auditor.auditor) }}</td>
            <td>{{ auditor.auditCount }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="user-filter">
      <h4>Find Search terms audited by User</h4>
      <div class="user-selector">
        <label for="selectUser">Select User:</label>
        <select v-model="selectedUser" id="selectUser">
          <option value="">All Users</option>
          <option
            v-for="userEmail in auditors"
            :key="userEmail"
            :value="userEmail"
          >
            {{ convertEmailToName(userEmail.auditor) }}
          </option>
        </select>
        <button @click="filterSearchTermsByUser">Apply</button>
      </div>
    </section>

    <!-- Display Search Terms by User -->
    <section
      v-if="selectedUser && auditedTerms.length"
      class="search-terms-by-user"
    >
      <h5>
        Search Terms Audited by {{ convertEmailToName(selectedUser.auditor) }}
      </h5>
      <ul>
        <li v-for="term in auditedTerms" :key="term">{{ term }}</li>
      </ul>
    </section>

    <section class="search-terms">
      <h4>Top Audit Search Terms</h4>
      <table class="search-terms-table">
        <thead>
          <tr>
            <th>Search Type</th>
            <th>Top Relevant Terms</th>
            <th>Top Irrelevant Terms</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Lexical</td>
            <td>
              <ul>
                <li v-for="term in topRelevantLexicalSearchTerms" :key="term">
                  {{ term }}
                </li>
              </ul>
            </td>
            <td>
              <ul>
                <li v-for="term in topIrrelevantLexicalSearchTerms" :key="term">
                  {{ term }}
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <td>Hybrid</td>
            <td>
              <ul>
                <li v-for="term in topRelevantHybridSearchTerms" :key="term">
                  {{ term }}
                </li>
              </ul>
            </td>
            <td>
              <ul>
                <li v-for="term in topIrrelevantHybridSearchTerms" :key="term">
                  {{ term }}
                </li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</template>

<style scoped>
* {
  --vdp-selected-bg-color: #0072ff;
  --vdp-hover-bg-color: #0072ff;
  --vdp-heading-hover-color: rgba(0, 114, 255, 0.05);
  outline: none;
  font-family: Source Sans Pro, sans-serif;
}
*:focus {
  outline: none;
}
.container {
  padding: 0px 80px;
  margin-top: 20px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

.auditor-table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 20px;
}

.auditor-table th {
  background-color: #0072ff;
  color: white;
  font-weight: bold;
  text-align: left;
}

.auditor-table th,
.auditor-table td {
  padding: 10px;
  border: 1px solid #ccc;
}

.auditor-table tbody tr:nth-child(even) {
  /* background-color: #f2f2f2; */
}
.search-terms-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.search-terms-table th {
  background-color: #0072ff;
  font-weight: bold;
  text-align: left;
  padding: 10px;
  color: white;
}

.search-terms-table th,
.search-terms-table td {
  border: 1px solid #ccc;
  padding: 10px;
}

.search-terms-table td ul {
  padding: 0;
  margin: 0;
  list-style: none;
}

.search-terms-table td ul li {
  margin-bottom: 5px;
}
.date-picker {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: small;
  font-family: Source Sans Pro, sans-serif;
}

.date-picker label {
  display: block;
  margin-bottom: 5px;
  font-family: Source Sans Pro, sans-serif;
}

.date-picker button {
  background-color: #0072ff;
  color: white;
  border-radius: 4px;
  padding: 2px 10px;
  border: none;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  height: 24px;
}

.date-picker button:hover {
  background-color: #0056c1;
}
.header {
  display: flex;
  width: 100%;
  justify-content: space-between;
}

.user-selector {
  display: flex;
  gap: 14px;
  padding: 24px 0;
  align-items: center;
  margin-top: 10px;
}

.user-selector label {
  margin-right: 14px;
  font-family: Source Sans Pro, sans-serif;
}

.user-selector select {
  height: 32px;
  width: 600px;
  border-radius: 4px;
  background-color: rgb(240, 242, 246);
  padding: 0px 8px;
  box-sizing: border-box;
  border: rgb(240, 242, 246);
  border-right: 16px solid transparent;
}

.user-selector button {
  background-color: #0072ff;
  color: white;
  border-radius: 4px;
  padding: 2px 10px;
  border: none;
  font-weight: 500;
  height: 30px;
  cursor: pointer;
}

.user-selector button:hover {
  background-color: #0056c1;
}
</style>
