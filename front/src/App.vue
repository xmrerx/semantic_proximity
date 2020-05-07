<template>
  <div class="container">
    <h1 class="title">
      Semantic Proximity
    </h1>
    <nav class="level app-levelbar">
      <breadcrumb :list="list"><breadcrumb>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import Breadcrumb from 'vue-bulma-breadcrumb'

export default {
  name: 'App',
  components: { Breadcrumb },
    computed: {
    list () {
      // todo: replace it with more general solution (rewrite Breadcrumb?)
      if (
          this.$route.matched.length == 2
          &&
          (this.$route.matched[0].path + '/' == this.$route.matched[1].path)
        ) {
        return [this.$route.matched[1]];
      } else {
        return this.$route.matched;
      }
    }
  }
};
</script>

<style scoped>
.breadcrumb {
  height: 40px;
  background-color: #f6f6f6;
  border-radius: 2px;
  padding: 0 10px 0 10px;
}
</style>