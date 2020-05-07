import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource';

import App from './App';
import TextsPage from './TextsPage';
import TextPage from './TextPage';

const NotFound = { template: '<p>Page not found</p>' }

const routes = [
  { meta: {label: 'Texts'}, path: '/texts', component: App, children: [
    { name: 'Text', path: ':id', component: TextPage, props: true },
    { name: 'Texts', path: '', component: TextsPage }, 
  ]},
  { path: '/', redirect: '/texts' },
  { path: '*', component: NotFound }
]

const router = new VueRouter({
  // mode: 'history',
  routes
});


Vue.use(VueRouter);
Vue.use(VueResource);

Vue.http.options.root = 'http://192.168.33.46:5000/';

new Vue({
  router,
  el: '#app',
  template: '<router-view/>'
})