import '../css/app.css';
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';

import { createApp, h } from 'vue';
import { createInertiaApp } from '@inertiajs/vue3';
import { createVuetify } from 'vuetify';
import { installRouteHelper } from './route';

installRouteHelper();

const vuetify = createVuetify({
    theme: {
        defaultTheme: 'light',
    },
});

createInertiaApp({
    title: (title) => (title ? `${title} — Student Clearance` : 'Student Clearance'),
    resolve: (name) => {
        const pages = import.meta.glob('./Pages/**/*.vue', { eager: true });
        return pages[`./Pages/${name}.vue`];
    },
    // Django's CSRF cookie/header names differ from Laravel's XSRF-TOKEN
    // convention — see https://github.com/inertiajs/inertia-django#csrf
    http: {
        xsrfCookieName: 'csrftoken',
        xsrfHeaderName: 'X-CSRFToken',
    },
    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .use(vuetify)
            .mount(el);
    },
});
