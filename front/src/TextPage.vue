<template>
<div class="columns is-multiline">
  <div class="column is-half">
    <div class="sentences">
      <a v-for="(sentence, index) in sentences"
         v-bind:key="index"
         v-bind:class="{ active: index == activeIndex }"
         @click="compare"
         :id="'sent-' + index">{{ sentence }}</a>
    </div>
  </div>
  <div class="column fix-rigth">        
    <table class="table is-narrow">
        <tr v-for="simmilar_sentece in simmilar_senteces"
            v-bind:key="simmilar_sentece.sentece_id">
          <td>
            <router-link :to="`/texts/${simmilar_sentece.text_id}`">
              <i class="fa fa-chevron-left"></i>
            </router-link>
          </td>
          <td>{{ simmilar_sentece.sentece }}</td>
          <td>{{ simmilar_sentece.similarity.toFixed(3) }}</td>
        </tr>
    </table>
  </div>
</div>
</template>

<script>
export default {
  name: "TextPage",
    data() {
    return {
        'sentences': [],
        'simmilar_senteces': [],
        'activeIndex': -1
    }},
  props: ['id'],
  mounted() {
    this.$http.get(`texts/${this.id}`).then(
      response => {
        this.sentences = response.body.split("\n");
      }, error => {
        console.log("Server error while getting text.");
      }
    );
  },
  methods: {
      compare(e) {
        this.activeIndex = e.currentTarget.id.replace('sent-', '');
        const sentence = this.sentences[this.activeIndex];
        this.$http.post(`texts/${this.id}/compare`, {sentence: sentence}).then(
          response => {
            this.simmilar_senteces = response.body;      
          }, error => {
            console.log("Server error while comparing.");
          }
        );
      }
  }
}
</script>

<style lang="scss" scoped>
@media only screen and (min-width: 769px) {
  .fix-rigth {
    overflow-y:scroll;
    box-sizing:border-box;
    background: #eee;
    position:fixed;
    top:0;
    left: 50%;
    height: 100%;
    width:50%;
  }
}
.sentences {
  a {
    color: #222;
    border-radius: 2px;
    padding: 0 5px 0 5px;
    &:hover {
      background-color: #eee;
    }
    &.active {
      background-color: #bed;
    }
  }
}
</style>