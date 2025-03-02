"use client";

import { Button } from "@heroui/button";
import { Card, CardBody, CardFooter, CardHeader } from "@heroui/card";
import { Divider } from "@heroui/divider";
import { Switch } from "@heroui/switch";
import { useTheme } from "next-themes";
import { useState, useEffect } from "react";

export default function ThemeTestPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Ensure component is mounted to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="flex flex-col gap-8 py-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold dark:text-white">Dark Mode Theme Test</h1>
        <p className="text-default-500 dark:text-gray-300">
          This page demonstrates the dark mode colors using Tailwind's dark: variant.
        </p>
      </div>

      <div className="flex gap-4 items-center">
        <span className="dark:text-white">Current theme: {theme}</span>
        <Button 
          color="primary" 
          variant="flat" 
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        >
          Toggle Theme
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Primary Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Primary Color</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using primary color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="primary">Primary Button</Button>
              <div className="w-full h-12 bg-primary rounded-lg flex items-center justify-center text-white">
                Primary Background
              </div>
              <p className="text-primary">Primary Text</p>
            </div>
          </CardBody>
        </Card>

        {/* Secondary Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Secondary Color</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using secondary color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="secondary">Secondary Button</Button>
              <div className="w-full h-12 bg-secondary rounded-lg flex items-center justify-center text-white">
                Secondary Background
              </div>
              <p className="text-secondary">Secondary Text</p>
            </div>
          </CardBody>
        </Card>

        {/* Success Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Success Color</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using success color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="success">Success Button</Button>
              <div className="w-full h-12 bg-success rounded-lg flex items-center justify-center text-white">
                Success Background
              </div>
              <p className="text-success">Success Text</p>
            </div>
          </CardBody>
        </Card>

        {/* Warning Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Warning Color</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using warning color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="warning">Warning Button</Button>
              <div className="w-full h-12 bg-warning rounded-lg flex items-center justify-center text-white">
                Warning Background
              </div>
              <p className="text-warning">Warning Text</p>
            </div>
          </CardBody>
        </Card>

        {/* Danger Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Danger Color</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using danger color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="danger">Danger Button</Button>
              <div className="w-full h-12 bg-danger rounded-lg flex items-center justify-center text-white">
                Danger Background
              </div>
              <p className="text-danger">Danger Text</p>
            </div>
          </CardBody>
        </Card>

        {/* Default Card */}
        <Card className="max-w-md dark:bg-gray-800">
          <CardHeader className="flex gap-3">
            <div className="flex flex-col">
              <p className="text-md dark:text-white">Default Colors</p>
              <p className="text-small text-default-500 dark:text-gray-300">Using default color scheme</p>
            </div>
          </CardHeader>
          <Divider/>
          <CardBody>
            <div className="flex flex-col gap-4">
              <Button color="default">Default Button</Button>
              <div className="w-full h-12 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center dark:text-white">
                Gray Background
              </div>
              <p className="text-gray-500 dark:text-gray-300">Gray Text</p>
              <Switch defaultSelected aria-label="Default switch" />
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
} 