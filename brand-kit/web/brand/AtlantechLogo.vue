<script setup>
// <AtlantechLogo />                                     primary logo, on a paper card in dark mode
// <AtlantechLogo shape="symbol" :height="32" />
// <AtlantechLogo shape="wordmark" tone="reversed" :height="28" />   directly on a navy bar
//
// Needs Vite (import.meta.glob) and css/tokens.css loaded once in the app.
import { computed } from 'vue'

const props = defineProps({
  shape: { type: String, default: 'lockup', validator: (v) => ['lockup', 'symbol', 'wordmark'].includes(v) },
  tone: { type: String, default: 'color', validator: (v) => ['color', 'auto', 'reversed', 'mono-navy', 'mono-white'].includes(v) },
  height: { type: [Number, String], default: 48 },
  cardOnDark: { type: Boolean, default: true },
  alt: { type: String, default: 'ATLANTECH' },
})

const logos = import.meta.glob('./logos/*.png', { eager: true, import: 'default' })
const src = (tone) => logos[`./logos/atlantech-${props.shape}-${tone}.png`]
const size = computed(() => (typeof props.height === 'number' ? `${props.height}px` : props.height))
const carded = computed(() => props.tone === 'color' && props.cardOnDark)
</script>

<template>
  <span class="atl-logo" :class="{ 'atl-logo--card': carded }" :style="{ height: size }">
    <template v-if="tone === 'auto'">
      <img :src="src('color')" :alt="alt" class="atl-logo__light" />
      <img :src="src('reversed')" alt="" aria-hidden="true" class="atl-logo__dark" />
    </template>
    <img v-else :src="src(tone)" :alt="alt" />
  </span>
</template>

<style scoped>
.atl-logo {
  display: inline-flex;
  align-items: center;
  box-sizing: content-box;
}
.atl-logo img {
  height: 100%;
  width: auto;
}
/* The card only shows in dark mode: tokens.css sets these to transparent / 0 in light mode */
.atl-logo--card {
  background: var(--atl-logo-card, transparent);
  padding: var(--atl-logo-card-pad, 0);
  border-radius: var(--atl-radius-lg, 16px);
}
.atl-logo__light { display: var(--atl-logo-light-display, inline); }
.atl-logo__dark { display: var(--atl-logo-dark-display, none); }
</style>
