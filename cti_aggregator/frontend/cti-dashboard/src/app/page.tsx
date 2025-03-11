"use client"

import { useState, useEffect } from "react";
import ThreatIntelligenceTable from "@/components/ThreatIntelligenceTable";
import CrowdStrikeMalwareTable from "@/components/CrowdStrikeMalwareTable";
import CrowdStrikeTailoredIntelTable from "@/components/CrowdStrikeTailoredIntelTable";
import CrowdStrikeActorsTable from "@/components/CrowdStrikeActorsTable";
import CISAKevTable from "@/components/CISAKevTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BackendConnectionCheck } from "@/components/BackendConnectionCheck";

export default function Home() {
  const [activeTab, setActiveTab] = useState("intelligence");
  const [isMounted, setIsMounted] = useState(false);

  // Use useEffect to mark component as mounted
  // This helps prevent hydration issues with client components
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Don't render tabs until client-side to avoid hydration issues
  if (!isMounted) {
    return (
      <main className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">CTI Dashboard</h1>
          <p className="text-gray-500 mt-2">Cyber Threat Intelligence Analysis Dashboard</p>
        </div>
        <div className="p-8 text-center">
          <div className="animate-pulse flex space-x-4">
            <div className="flex-1 space-y-6 py-1">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-4 bg-gray-200 rounded col-span-2"></div>
                  <div className="h-4 bg-gray-200 rounded col-span-1"></div>
                </div>
                <div className="h-4 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">CTI Dashboard</h1>
        <p className="text-gray-500 mt-2">Cyber Threat Intelligence Analysis Dashboard</p>
      </div>
      
      <BackendConnectionCheck />
      
      <Tabs defaultValue="intelligence" value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="intelligence">Threat Intelligence</TabsTrigger>
          <TabsTrigger value="tailored-intel">CrowdStrike Tailored Intel</TabsTrigger>
          <TabsTrigger value="actors">CrowdStrike Actors</TabsTrigger>
          <TabsTrigger value="malware">CrowdStrike Malware</TabsTrigger>
          <TabsTrigger value="indicators">CrowdStrike Indicators</TabsTrigger>
          <TabsTrigger value="rules">CrowdStrike Rules</TabsTrigger>
          <TabsTrigger value="kev">CISA KEV</TabsTrigger>
        </TabsList>
        <div className="mt-6">
          <TabsContent value="intelligence">
            <ThreatIntelligenceTable key="intelligence-table" />
          </TabsContent>
          <TabsContent value="tailored-intel">
            <CrowdStrikeTailoredIntelTable key="tailored-intel-table" />
          </TabsContent>
          <TabsContent value="actors">
            <CrowdStrikeActorsTable key="actors-table" />
          </TabsContent>
          <TabsContent value="malware">
            <CrowdStrikeMalwareTable key="malware-table" />
          </TabsContent>
          <TabsContent value="indicators">
            <div className="p-8 text-center">
              <h2 className="text-xl font-semibold mb-4">CrowdStrike Indicators</h2>
              <p className="text-gray-500">
                This feature is coming soon. It will display indicators of compromise (IOCs) from CrowdStrike.
              </p>
            </div>
          </TabsContent>
          <TabsContent value="rules">
            <div className="p-8 text-center">
              <h2 className="text-xl font-semibold mb-4">CrowdStrike Rules</h2>
              <p className="text-gray-500">
                This feature is coming soon. It will display detection rules from CrowdStrike.
              </p>
            </div>
          </TabsContent>
          <TabsContent value="kev">
            <CISAKevTable key="kev-table" />
          </TabsContent>
        </div>
      </Tabs>
    </main>
  );
}
