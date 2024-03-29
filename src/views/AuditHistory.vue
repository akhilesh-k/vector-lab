<script setup>
import { ref, onMounted, computed } from "vue";
import DatePicker from "vue3-datepicker";
import { format } from "date-fns";

const startDate = ref(null);
const endDate = ref(null);
const apiUrl = "http://xsearch-solr-vector-2.qa2-sg.cld:5000";

const defaultStartDate = new Date();
defaultStartDate.setDate(defaultStartDate.getDate() - 7);
startDate.value = defaultStartDate;
endDate.value = new Date();

const selectedUser = ref(localStorage.getItem("auditorEmail") || "");
const auditorEmail = localStorage.getItem("auditorEmail");
const auditedTerms = ref([]);
const auditors = ref([]);
const topRelevantLexicalSearchTerms = ref([]);
const topRelevantHybridSearchTerms = ref([]);
const topIrrelevantLexicalSearchTerms = ref([]);
const topIrrelevantHybridSearchTerms = ref([]);
const auditorSearchTermPage = ref(0);
const pageSize = 10;
const currentPage = ref(0);
const searchTerm = ref("");
const auditCampaigns = ref({});

const auditRelevanceSet = ref(
  JSON.parse(
    localStorage.getItem(
      `auditRelevanceSet_${formatDate(startDate.value)}_${formatDate(
        endDate.value
      )}`
    )
  ) || []
);

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
const displayedAuditRelevanceSet = computed(() => {
  const startIndex = currentPage.value * pageSize;
  const endIndex = startIndex + pageSize;
  const filteredSet = auditRelevanceSet.value.filter((item) =>
    item.searchTerm.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
  return filteredSet.slice(startIndex, endIndex);
});

const showNextButton = computed(() => {
  return currentPage.value * pageSize < auditRelevanceSet.value.length;
});

const showNextSet = () => {
  currentPage.value++;
};

const applyDateFilter = async () => {
  try {
    const filterUrl = `${apiUrl}/fetch-auditors?start_date=${formatDate(
      startDate.value
    )}&end_date=${formatDate(endDate.value)}`;
    const response = await fetch(filterUrl);
    const data = await response.json();
    auditors.value = data.auditors;
    filterSearchTermsByUser(false);
    fetchAuditRelevanceSet();
  } catch (error) {
    console.error("Error:", error);
  }
};

const convertEmailToName = (email) => {
  const parts = email.split("@")[0].split(".");
  return parts
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};

const fetchAuditCampaign = async () => {
  try {
    const response = await fetch(`${apiUrl}/get-audit-campaigns`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    auditCampaigns.value = data;
  } catch (error) {
    // Handle errors
    console.error("Error fetching data:", error.message);
    throw error; // Re-throw the error to allow handling it at the caller's level
  }
};

const fetchAuditRelevanceSet = async () => {
  try {
    const startDateFormat = formatDate(startDate.value);
    const endDateFormat = formatDate(endDate.value);
    const localStorageKey = `auditRelevanceSet_${startDateFormat}_${endDateFormat}`;

    // Check if the data is already in local storage
    const storedData = localStorage.getItem(localStorageKey);

    if (storedData) {
      // If data is in local storage, use it and update your state
      const parsedData = JSON.parse(storedData);
      auditRelevanceSet.value = parsedData;
    } else {
      // If data is not in local storage, make the API call
      const response = await fetch(
        `${apiUrl}/relevant_counts?start_date=${startDateFormat}&end_date=${endDateFormat}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      // Store the response in local storage
      localStorage.setItem(localStorageKey, JSON.stringify(data));

      // Update your state or do any other necessary tasks
      auditRelevanceSet.value = data;
    }
  } catch (error) {
    console.error("Error fetching audit relevance set:", error);
    // Handle errors as needed
  }
};

const filterSearchTermsByUser = async (isNextPage) => {
  if (isNextPage) {
    auditorSearchTermPage.value += 1;
  }
  try {
    if (selectedUser.value) {
      let filterSearchTermByUserUrl = `${apiUrl}/fetch-audited-terms?auditor=${
        selectedUser.value.auditor === undefined
          ? selectedUser.value
          : selectedUser.value.auditor
      }&page=${auditorSearchTermPage.value}&per_page=${30}`;
      if (startDate.value && endDate.value) {
        filterSearchTermByUserUrl = `${filterSearchTermByUserUrl}&start_date=${formatDate(
          startDate.value
        )}&end_date=${formatDate(endDate.value)}`;
      }
      const response = await fetch(filterSearchTermByUserUrl);
      const data = await response.json();
      auditedTerms.value = data.audited_terms;
    } else {
      auditedTerms.value = [];
    }
  } catch (error) {
    console.error("Error filtering search terms by user:", error);
    auditedTerms.value = [];
  }
};

onMounted(async () => {
  fetchAuditCampaign();
  try {
    const auditorsResponse = await fetch(
      `${apiUrl}/fetch-auditors?start_date=${formatDate(
        startDate.value
      )}&end_date=${formatDate(endDate.value)}`
    );
    const auditorsData = await auditorsResponse.json();
    auditors.value = auditorsData.auditors;
    const searchTermsResponse = await fetch(`${apiUrl}/fetch-top-search-terms`);
    const searchTermsData = await searchTermsResponse.json();
    topRelevantLexicalSearchTerms.value =
      searchTermsData.topRelevantLexicalSearchTerms;
    topRelevantHybridSearchTerms.value =
      searchTermsData.topRelevantHybridSearchTerms;
    topIrrelevantLexicalSearchTerms.value =
      searchTermsData.topIrrelevantLexicalSearchTerms;
    topIrrelevantHybridSearchTerms.value =
      searchTermsData.topIrrelevantHybridSearchTerms;
    filterSearchTermsByUser();
    fetchAuditRelevanceSet();
  } catch (error) {
    console.error("Error fetching data:", error);
  }
});
</script>

<template>
  <main class="container">
    <section v-if="auditCampaigns.length">
      <h3>Live Audit Campaign</h3>
      <table>
        <thead>
          <tr>
            <th>Campaign ID</th>
            <th>Auditors</th>
            <th>Audit Size</th>
            <th>Owner</th>
            <th>Start Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="auditCampaign in auditCampaigns" :key="auditCampaign._id">
            <td>{{ auditCampaign.campaign_id }}</td>
            <td>
              <ul>
                <li v-for="auditor in auditCampaign.auditors" :key="auditor">
                  {{ convertEmailToName(auditor) }}
                </li>
              </ul>
            </td>
            <td>{{ convertEmailToName(auditCampaign.owner) }}</td>
            <td>{{ auditCampaign.start_date }}</td>
            <td>{{ auditCampaign.audit_size }}</td>
            <td>{{ auditCampaign.status }}</td>
          </tr>
        </tbody>
      </table>
    </section>
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
            <th>Lexical Audit Count</th>
            <th>Hybrid Audit Count</th>
            <th>Total Audit Count</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="auditor in auditors" :key="auditor.auditor">
            <td>{{ convertEmailToName(auditor.auditor) }}</td>
            <td>{{ auditor.lexical_count }}</td>
            <td>{{ auditor.hybrid_count }}</td>
            <td>{{ auditor.total_audit }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="user-filter">
      <h4>Find Search terms audited by User</h4>
      <div class="user-selector">
        <label for="selectUser">Select User:</label>
        <select v-model="selectedUser" id="selectUser">
          <option v-if="auditorEmail" :value="auditorEmail">
            {{ convertEmailToName(auditorEmail) }}
          </option>
          <option
            v-for="userEmail in auditors"
            :key="userEmail"
            :value="userEmail"
          >
            {{ convertEmailToName(userEmail.auditor) }}
          </option>
        </select>
        <button @click="filterSearchTermsByUser(false)">Apply</button>
      </div>
    </section>

    <!-- Display Search Terms by User -->
    <div v-if="!auditedTerms.length && (selectedUser.auditor || auditorEmail)">
      No search Terms found for the Auditor:
      {{
        selectedUser.auditor
          ? convertEmailToName(selectedUser.auditor)
          : auditorEmail
          ? convertEmailToName(auditorEmail)
          : ""
      }}
      in the selected period. Try increasing the date filter range.
    </div>
    <section v-if="auditedTerms.length" class="audited-terms">
      <h5>
        Audited Search Terms by
        {{
          selectedUser.auditor
            ? convertEmailToName(selectedUser.auditor)
            : auditorEmail
            ? convertEmailToName(auditorEmail)
            : ""
        }}
      </h5>
      <div class="audited-search-terms">
        <div v-for="auditedTerm in auditedTerms" :key="auditedTerm._id">
          <strong>{{ auditedTerm._id }}</strong>
          <p class="searchterm-count">
            Displaying {{ Math.min(auditedTerm.count, 30) }} out of
            {{ auditedTerm.count }} audited search terms for
            {{ auditedTerm._id }} results Auditing.
          </p>
          <div>
            <p v-for="term in auditedTerm.audited_terms" :key="term">
              {{ term }}
            </p>
          </div>

          <p class="searchterm-count">
            Page {{ auditorSearchTermPage + 1 }} out of
            {{ Math.ceil(auditedTerm.count / 30) }}
          </p>
          <p class="searchterm-count" style="color: red">
            Kindly excuse the button disabling logic for now. Will add the
            support later!
          </p>
        </div>
      </div>
      <button v-if="auditedTerms" @click="filterSearchTermsByUser(true)">
        See Next ➔
      </button>
    </section>
    <section>
      <h4>Audited Search Terms - Relevance Set</h4>
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Type a search term to filter the data in the table!"
      />
      <table class="auditor-table">
        <thead>
          <tr>
            <th rowspan="2">Search Term</th>
            <th colspan="2">Lexical</th>
            <th colspan="2">Hybrid</th>
            <th rowspan="2">Auditor</th>
          </tr>
          <tr>
            <th>Relevant</th>
            <th>Irrelevant</th>
            <th>Relevant</th>
            <th>Irrelevant</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in displayedAuditRelevanceSet" :key="index">
            <td>{{ item.searchTerm }}</td>
            <td>{{ item.relevantCountLexical }}</td>
            <td>{{ item.irrelevantCountLexical }}</td>
            <td>{{ item.relevantCountHybrid }}</td>
            <td>{{ item.irrelevantCountHybrid }}</td>
            <td>{{ convertEmailToName(item.auditor) }}</td>
          </tr>
        </tbody>
      </table>
      <button
        @click="showNextSet"
        v-if="showNextButton"
        style="margin-top: 16px"
      >
        Show next 10 item
      </button>
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
button {
  background-color: #0072ff;
  color: white;
  border-radius: 4px;
  padding: 2px 10px;
  border: none;
  font-weight: 500;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
button:disabled {
  background-color: #adc9ec;
  cursor: not-allowed;
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
.audited-search-terms {
  display: flex;
  justify-content: space-between;
}
input[type="text"] {
  height: 32px;
  border-radius: 4px;
  background-color: rgb(240, 242, 246);
  padding: 0px 8px;
  box-sizing: border-box;
  border: rgb(240, 242, 246);
  width: 500px;
}
.searchterm-count {
  font-size: 13px;
  color: #0072ff;
}
table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

/* Styling for the list of auditors */
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

li {
  margin-bottom: 4px;
}
</style>
