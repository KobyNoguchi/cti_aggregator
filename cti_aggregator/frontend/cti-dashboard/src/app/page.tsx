"use client"

import { useState } from "react";
import ThreatIntelligenceTable from "@/components/ThreatIntelligenceTable";
import CrowdStrikeMalwareTable from "@/components/CrowdStrikeMalwareTable";
import CrowdStrikeTailoredIntelTable from "@/components/CrowdStrikeTailoredIntelTable";
import CrowdStrikeActorsTable from "@/components/CrowdStrikeActorsTable";
import CISAKevTable from "@/components/CISAKevTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Home() {
  const [activeTab, setActiveTab] = useState("intelligence");

  return (
    <main className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">CTI Dashboard</h1>
        <p className="text-gray-500 mt-2">Cyber Threat Intelligence Analysis Dashboard</p>
      </div>
      
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
            <ThreatIntelligenceTable />
          </TabsContent>
          <TabsContent value="tailored-intel">
            <CrowdStrikeTailoredIntelTable />
          </TabsContent>
          <TabsContent value="actors">
            <CrowdStrikeActorsTable />
          </TabsContent>
          <TabsContent value="malware">
            <CrowdStrikeMalwareTable />
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
            <CISAKevTable />
          </TabsContent>
        </div>
      </Tabs>
    </main>
  );
}
