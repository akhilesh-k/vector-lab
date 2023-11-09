<script setup>
import { ref, onMounted } from "vue";

const auditors = ref([]);
const topRelevantLexicalSearchTerms = ref([]);
const topRelevantHybridSearchTerms = ref([]);

const topIrrelevantLexicalSearchTerms = ref([]);
const topIrrelevantHybridSearchTerms = ref([]);

const convertEmailToName = (email) => {
  const parts = email.split("@")[0].split(".");
  return parts
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
};
const apiUrl = "http://xsearch-solr-vector-2.qa2-sg.cld:5000";

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
    <h3>Audit Reports and History</h3>

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
</style>
