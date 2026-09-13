// Tiny stand-in for Laravel's Ziggy `route()` helper, so the Vue pages
// (ported unchanged from the Laravel version) can keep calling the bare
// global `route(name, id)` without knowing the backend changed.
const routes = {
    login: '/login',
    logout: '/logout',
    'student.dashboard': '/student/dashboard',
    'student.clearance.create': '/student/clearance/create',
    'student.clearance.store': '/student/clearance',
    'student.clearance.show': '/student/clearance/{id}',
    'student.approvals.resubmit': '/student/approvals/{id}/resubmit',
    'approver.dashboard': '/approver/dashboard',
    'approver.approvals.show': '/approver/approvals/{id}',
    'approver.approvals.update': '/approver/approvals/{id}',
    'assistant.chat': '/assistant/chat',
    'assistant.status': '/assistant/status',
};

export function route(name, param) {
    const template = routes[name];
    if (!template) {
        throw new Error(`Unknown route: ${name}`);
    }
    return param !== undefined ? template.replace('{id}', param) : template;
}

export function installRouteHelper() {
    window.route = route;
}
