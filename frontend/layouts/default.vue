<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { useUsersLogout } from '~/api'

const queryClient = useQueryClient()
const { me, meLoading } = useMe()
const logout = useUsersLogout({
  mutation: {
    onSuccess: () => {
      queryClient.clear()
      queryClient.invalidateQueries()
      location.reload()
    },
  },
})
function handleLogout() {
  logout.mutate()
}

const colorMode = useColorMode()
const isDark = computed({
  get() {
    return colorMode.value === 'dark'
  },
  set() {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
  },
})

function handleThemeToggle() {
  isDark.value = !isDark.value
}
</script>

<template>
  <div class="py-4">
    <header>
      <UContainer>
        <Card class="px-4 py-2 flex mb-4 items-center justify-between">
          <UHorizontalNavigation
            :links="[
              { label: 'Главная', to: '/' },
              { label: 'ВУЗы', to: '/orgs' },
              { label: 'Чаты', to: '/chats' },
              ...((me?.role === 'admin' || me?.role === 'moderator') ? [{ label: 'Модерация', to: '/moderator' }] : []),
            ]"
          />
          <div class="flex items-center">
            <UButton v-if="meLoading" loading variant="outline" label="Профиль" />
            <UDropdown
              v-else-if="me"
              mode="hover"
              :items="[
                [
                  { label: 'Профиль', icon: 'i-heroicons-user-circle', href: '/profile' },
                  { label: 'Тёмная тема', icon: isDark ? 'i-heroicons-moon' : 'i-heroicons-sun', click: handleThemeToggle },
                ],
                [{ label: 'Выйти', icon: 'i-heroicons-arrow-right-start-on-rectangle', click: handleLogout, disabled: logout.isPending.value }],
              ]"
            >
              <UButton color="white" label="Профиль" trailing-icon="i-heroicons-chevron-down-20-solid" />
            </UDropdown>
            <NuxtLink v-else to="/login">
              <UButton icon="i-octicon-sign-in-16" variant="outline" label="Войти" />
            </NuxtLink>
          </div>
        </Card>
      </UContainer>
    </header>
    <main>
      <slot />
    </main>
  </div>
</template>
