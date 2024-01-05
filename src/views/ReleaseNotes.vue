<script setup>
import { useRouter } from "vue-router";
const router = useRouter();

const pushToRoute = (route) => {
  router.push(route);
};
</script>
<template>
  <main class="container">
    <h3>Release Notes</h3>
    <section class="release-note">
      <h4>Version 2.0.0</h4>
      <h5>5th January 2023</h5>
      <p>Create Audit campaigns and assign auditor by xlsx file upload.</p>
      <ul>
        <li>
          Now we can create audit campaigns and assigna the auditor using the
          <span. class="url" @click="pushToRoute('/assign-audits')"
            >Assign Audit</span.
          >
          page in the Vector lab!
        </li>
      </ul>
      <h4>Version 1.7.0</h4>
      <h5>4th January 2023</h5>
      <p>Use Variant 3 as the default algo.</p>
      <ul>
        <li>Vector lab now uses the variant3 as the default AB algo.</li>
      </ul>
      <h4>Version 1.6.0</h4>
      <h5>6th December 2023</h5>
      <p>Now we can compare the lexical, hybrid and pure vector results.</p>
      <ul>
        <li>
          Select Vector Search in the lab page and now get the pure vector
          results listed on the page!
        </li>
      </ul>
      <h4>Version 1.5.0</h4>
      <h5>17th November 2023</h5>
      <p>Now you can see the audit results on the Audit History page.</p>
      <ul>
        <li>
          Audit Results: You can see audited search terms on the audit history
          page now.
        </li>
        <li>
          Search audited search terms: You can search for audited search terms
          by typing in the search bar available above the table! You know, for
          Search!
        </li>
      </ul>

      <h4>Version 1.4.0</h4>
      <h5>14th November 2023</h5>
      <p>
        Now date filters can be applied to find the search terms audited by
        auditors within a time period.
      </p>
      <ul>
        <li>
          Audit Progress: Now see the auditing progress via Audited search
          term's count for Lexical and Hybrid.
        </li>
        <li>
          Auditor's search term: Lexical and Hybrid search terms are displayed
          in separate layouts.
        </li>
        <li>
          Date Range filter: Along with the audit count, date range filters can
          be applied to the search terms.
        </li>
      </ul>
      <p>Bug Fixes:</p>
      <ul>
        <li>
          Date Range filter: Issues while applying the date range filters on the
          audit count are now fixed.
        </li>
      </ul>
      <h4>Version 1.3.0</h4>
      <h5>10th November 2023</h5>
      <p>Now which search terms are audited by auditors can be found</p>
      <ul>
        <li>
          Audit Report: We can see the auditor's search terms by filtering by
          Auditor's name.
        </li>
        <li>
          Date Range filter: We have given a date range filter on the Audit
          report page to filter the results based on the date range selected.
        </li>
        <li>
          Pilihan Blibli: Now we can see the Manual merchandised products tag in
          the product card.
        </li>
      </ul>
      <p>Bug Fixes:</p>
      <ul>
        <li>
          Audit mode checkbox while navigating from Sidebar: In case of
          navigating to the perform Audit page from the vector search page,
          audit mode checkbox was not selected by default. This issue has been
          fixed in the 10th November deployment.
        </li>
      </ul>

      <h4>Version 1.2.0</h4>
      <h5>9th November 2023</h5>
      <p>We are excited to introduce the following features:</p>
      <ul>
        <li>
          Audit Report: Now we can see the Auditors and the Audit history they
          have done. This can be accessed by
          <span. class="url" @click="pushToRoute('/audit-history')"
            >clicking here</span.
          >
        </li>
        <li>
          Top Audited Search terms: Now we can see the top audited search terms
          for lexical and hybrid search types. We can also see the top search
          terms where the search results or Relevant or Irrelevant
        </li>
      </ul>

      <h4>Version 1.1.0</h4>
      <h5>8th November 2023</h5>
      <p>
        There has been a couple of improvements in the Overall UI. Below are the
        gist of the changes:
      </p>
      <ul>
        <li>
          Navigation Sidebar: Have added sidebar for navigation and can be
          accessed by clicking the left top button.
        </li>
        <li>
          Separated Vector Search and Audit Space: Now for the ease of the
          auditing processes, we are segregating the Vector search and the
          Auditing page.
        </li>
        <li>
          Reduced configuration elements for Audit mode: Perform audit has fewer
          options to configure, namely Algo, debug (just in case we want to
          check the scores).
        </li>
        <li>
          Relevant and Irrelevant result counts: In the backend, we are now
          saving the count of relevant and irrelevant products so that we can
          further create any sort of visualizations from the audit data.
        </li>
      </ul>
      <p>Bug Fixes:</p>
      <ul>
        <li>
          No result page leading to white screen: In case of no result pages,
          vector lab would run into an issue where only blank page was shown. We
          have now fixed it and it has very descriptive details.
        </li>
      </ul>

      <h4>Version 1.0.0</h4>
      <h5>30th October 2023</h5>
      <p>
        Auditing beta version is now available and Blibli Vector Lab has moved
        to Vue based UI for stability and control ✅
      </p>
      <ul>
        <li>
          Streamlit helped to rapidly develop the concept and now for more
          control and features, we have moved the UI to VueJs application.
        </li>
        <li>
          Audit checkbox: Now we can mark the relevance of products (audit) on
          the UI with the comments.
        </li>
        <li>
          Download Audit details in excel sheet: Clicking on submit audit will
          download the excel file and save the audit data with many details,
          like audit date, algo, search term, NDCG score, auditor, audited
          products
        </li>
      </ul>

      <h4>Version 0.5.0</h4>
      <h5>19th October 2023</h5>
      <p>Now seeing the Solr relevance and Vector score is made easy:</p>
      <ul>
        <li>
          Debug Checkbox: Added support to display the total score and vector
          boost when debug checkbox is ticked.
        </li>
      </ul>

      <h4>Version 0.4.0</h4>
      <h5>18th October 2023</h5>
      <p>Now see hybrid search for various A/B algorithms</p>
      <ul>
        <li>
          A/B algorithms: We can configure the search results to include
          different A/B algos available.
        </li>
      </ul>

      <h4>Version 0.3.0</h4>
      <h5>17th October 2023</h5>
      <p>Now Vector search is configurable from the UI</p>
      <ul>
        <li>
          Configure vector search params from the Vector lab: We can configure
          the params like, topK, boostValue, unionSize
        </li>
      </ul>

      <h4>Version 0.2.0</h4>
      <h5>15th October 2023</h5>
      <p>Clicking on product cards now take you to the PDP</p>
      <ul>
        <li>
          Products to PDP: Once a product is clicked, we form the PDP url and
          open the details for you.
        </li>
      </ul>

      <h4>Version 0.1.0</h4>
      <h5>12th October 2023</h5>
      <p>Swimlane UI is deployed</p>
      <ul>
        <li>
          Query products with lexical flow: We can enter a search term and
          search for the products using the production "/products" API
        </li>
        <li>
          Query products with hybrid flow : Vector Search results can now be
          passed to the Solr and we can fetch the boosted result set.
        </li>
      </ul>
    </section>

    <!-- Add more release notes sections for other versions here -->
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
  margin-top: 10px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.release-note {
  margin-bottom: 40px;
}
h2 {
  font-size: 1.5em;
  margin-bottom: 10px;
  color: #333; /* Customize the color */
}
p {
  margin: 10px 0;
  line-height: 1.6;
}
ul {
  margin: 10px 0;
  padding-left: 20px;
}
li {
  padding: 4px 0;
  margin: 5px 0;
}
.url {
  cursor: pointer;
  color: #0072ff;
  text-decoration: underline;
}

.url:hover {
  color: darkblue;
}
</style>
