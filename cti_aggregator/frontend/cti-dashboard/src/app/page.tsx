"use client"

import { useState } from "react";
import ThreatIntelligenceTable from "@/components/ThreatIntelligenceTable";
import CrowdStrikeMalwareTable from "@/components/CrowdStrikeMalwareTable";
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
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="intelligence">Threat Intelligence</TabsTrigger>
          <TabsTrigger value="malware">CrowdStrike Malware</TabsTrigger>
          <TabsTrigger value="kev">CISA KEV</TabsTrigger>
        </TabsList>
        <div className="mt-6">
          <TabsContent value="intelligence">
            <ThreatIntelligenceTable />
          </TabsContent>
          <TabsContent value="malware">
            <CrowdStrikeMalwareTable />
          </TabsContent>
          <TabsContent value="kev">
            <CISAKevTable />
          </TabsContent>
        </div>
      </Tabs>
    </main>
  );
}
