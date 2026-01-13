'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PostGenerator } from "@/components/post-generator"
import { PostLibrary } from "@/components/post-library"
import { Analytics } from "@/components/analytics"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            LinkedIn Post Factory
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Generate, manage, and analyze your LinkedIn content
          </p>
        </header>

        <Tabs defaultValue="generate" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="generate">Generate</TabsTrigger>
            <TabsTrigger value="library">Library</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-4">
            <PostGenerator />
          </TabsContent>

          <TabsContent value="library" className="space-y-4">
            <PostLibrary />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Analytics />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
