<script setup>
import { ref, computed, nextTick } from 'vue';
import { getJson, postJson } from '../csrf';

const open = ref(false);
const input = ref('');
const loading = ref(false);
const messages = ref([]);
const scrollArea = ref(null);

// null = checking, true = connected, false = confirmed unreachable.
// Checked fresh each time the panel opens, since Ollama may have gone
// down (or come back up) since the last time it was checked.
const connected = ref(null);
const inputDisabled = computed(() => loading.value || connected.value !== true);

async function checkConnection() {
    connected.value = null;
    try {
        const data = await getJson(route('assistant.status'));
        connected.value = data.connected;
    } catch {
        connected.value = false;
    }
}

function toggle() {
    open.value = !open.value;
    if (open.value) {
        checkConnection();
    }
}

async function scrollToBottom() {
    await nextTick();
    if (scrollArea.value) {
        scrollArea.value.scrollTop = scrollArea.value.scrollHeight;
    }
}

async function send() {
    const question = input.value.trim();
    if (!question || inputDisabled.value) return;

    messages.value.push({ role: 'user', text: question });
    input.value = '';
    loading.value = true;
    scrollToBottom();

    try {
        const data = await postJson(route('assistant.chat'), { message: question });
        messages.value.push({ role: 'assistant', text: data.answer, sources: data.sources });
    } catch (error) {
        messages.value.push({ role: 'assistant', text: error.message, isError: true });
    } finally {
        loading.value = false;
        scrollToBottom();
    }
}
</script>

<template>
    <div>
        <v-btn
            icon="mdi-robot"
            color="indigo-darken-2"
            size="large"
            style="position: fixed; bottom: 24px; right: 24px; z-index: 10"
            @click="toggle"
        />

        <v-card
            v-if="open"
            style="position: fixed; bottom: 96px; right: 24px; width: 360px; max-height: 480px; z-index: 10; display: flex; flex-direction: column"
            elevation="8"
        >
            <v-card-title class="d-flex align-center justify-space-between bg-indigo-darken-2" style="color: white">
                Clearance Assistant
                <v-btn icon="mdi-close" size="small" variant="text" style="color: white" @click="toggle" />
            </v-card-title>

            <div ref="scrollArea" class="pa-3" style="flex: 1; overflow-y: auto; min-height: 240px">
                <v-alert v-if="connected === false" type="warning" density="compact" variant="tonal" class="mb-3">
                    The Clearance Assistant is currently unavailable — the AI server isn't reachable
                    right now. Please try again later.
                </v-alert>

                <p v-if="messages.length === 0 && connected !== false" class="text-caption text-medium-emphasis">
                    Ask about clearance requirements, e.g. "What do I need for library clearance?"
                </p>

                <div v-for="(message, index) in messages" :key="index" class="mb-3">
                    <div
                        :class="message.role === 'user' ? 'text-right' : 'text-left'"
                        class="d-flex"
                        :style="{ justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start' }"
                    >
                        <div
                            class="pa-2 rounded"
                            :style="{
                                maxWidth: '85%',
                                background: message.role === 'user' ? '#e8eaf6' : message.isError ? '#ffebee' : '#f5f5f5',
                            }"
                        >
                            <span class="text-body-2">{{ message.text }}</span>

                            <div v-if="message.sources?.length" class="mt-2">
                                <v-chip
                                    v-for="source in message.sources"
                                    :key="source.title"
                                    size="x-small"
                                    class="mr-1 mb-1"
                                    variant="outlined"
                                >
                                    {{ source.title }} · {{ source.score }}
                                </v-chip>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="loading" class="d-flex justify-start">
                    <v-progress-circular indeterminate size="16" width="2" color="indigo-darken-2" />
                </div>
            </div>

            <v-divider />

            <div class="pa-2 d-flex">
                <v-text-field
                    v-model="input"
                    :placeholder="connected === false ? 'Assistant unavailable' : 'Ask a question...'"
                    density="compact"
                    variant="outlined"
                    hide-details
                    :disabled="inputDisabled"
                    @keyup.enter="send"
                />
                <v-btn class="ml-2" color="indigo-darken-2" icon="mdi-send" :disabled="inputDisabled" @click="send" />
            </div>
        </v-card>
    </div>
</template>
