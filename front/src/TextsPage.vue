<template>
<div class="columns is-multiline">
  <div class="column is-half">
    <form @submit="checkInput" method="post">
      <input type="submit" value="Process the new text" class="button is-primary"><br/>
      <p v-if="adding_error" class="error">
      {{ adding_error }}
      </p>
      <textarea v-model="text"
                placeholder="Put some text and click Process button."></textarea>
    </form>
  </div>
  <div class="column">
    <p class="subtitle">Loaded texts:</p>
    <table class="table is-narrow hidden-wrap">
        <tr v-for="text in texts" v-bind:key="text.id">
          <td><router-link :to="`/texts/${text.id}`">{{ text.title }}</router-link></td>
        </tr>
    </table>
  </div>
</div>
</template>

<script>
export default {
  name: "TextsPage",
  methods: {
    checkInput(e) {
      e.preventDefault();
      if (!this.text) {
        this.adding_error = "Text is required to continue.";
      } else {
        this.$http.post("texts", {"text": this.text}).then(
          response => {
            if (!response.body.hasOwnProperty('file')) {
              if (response.body.hasOwnProperty('error')) {
                this.adding_error = response.body.error;
              } else {
                this.adding_error = 'Unknown error uppeared.';
              }
            } else {
              this.adding_error = '';
              this.$router.push(`/texts/${response.body.file}`);
            }         
          }, error => {
            this.adding_error = "Server error.";
          }
        );
      }
    },
  },
  data() {
    return {
      adding_error: '',
      text: '',
      texts: [],
    };
  },
  mounted() {
    this.$http.get("texts").then(
      response => {
        this.texts = response.body;
      }, error => {
        console.log("Server error while getting texts.");
      }
    );
  }
}
</script>

<style lang="scss" scoped>
.error {
  color: #d44;
}
.column textarea {
  width: 100%;
  min-height: 200px;
  margin-top: 3px;
}
.hidden-wrap td {
  max-width: 300px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}
</style>