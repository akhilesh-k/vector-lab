import { createRouter, createWebHistory } from "vue-router";
import { useRouter } from "vue-router";
import Products from "@/views/Products.vue";
import Configure from "@/views/Configure.vue";
import AuditHistory from "@/views/AuditHistory.vue";
import ReleaseNotes from "@/views/ReleaseNotes.vue";
const router = useRouter();

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/vector-search",
      component: Products,
    },
    {
      name: "Vector Search",
      path: "/",
      meta: {
        audit: false,
        vectorSearch: true,
      },
      redirect: () => {
        return "/vector-search";
      },
    },
    {
      name: "Submit Audit",
      path: "/audit",
      meta: {
        audit: true,
        vectorSearch: false,
      },
      component: Products,
    },
    {
      name: "Audit History",
      path: "/audit-history",
      component: AuditHistory,
    },
    {
      path: "/configure",
      component: Configure,
    },
    {
      path: "/release-notes",
      component: ReleaseNotes,
    },
  ],
});
router.beforeEach((to, from, next) => {
  setRouteMetaData(to)
});
