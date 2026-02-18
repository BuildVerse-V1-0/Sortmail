'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { User, Mail, Brain, Palette, Check, Plus, AlertCircle } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="max-w-4xl mx-auto py-8 px-6 space-y-8 pb-20">

            {/* Profile Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                        <User className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Profile</h2>
                        <p className="text-sm text-ink-light">Manage your personal information</p>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-6">
                            <Avatar className="h-20 w-20 border-2 border-border-light">
                                <AvatarImage src="/placeholder-user.jpg" />
                                <AvatarFallback className="bg-primary/5 text-primary text-xl font-display">JD</AvatarFallback>
                            </Avatar>
                            <div className="space-y-4 flex-1 max-w-md">
                                <div className="grid gap-2">
                                    <Label htmlFor="name">Display Name</Label>
                                    <Input id="name" defaultValue="John Doe" className="bg-paper" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input id="email" defaultValue="you@company.com" disabled className="bg-paper-mid opacity-70" />
                                </div>
                            </div>
                            <div className="ml-auto self-start">
                                <Button>Save Changes</Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </section>

            <Separator />

            {/* Integrations Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-accent/10 rounded-xl flex items-center justify-center text-accent">
                        <Mail className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Integrations</h2>
                        <p className="text-sm text-ink-light">Connect your email providers</p>
                    </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                    {/* Gmail - Connected */}
                    <Card className="border-l-4 border-l-success">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 bg-white rounded-full border border-border-light flex items-center justify-center p-2">
                                        <img src="https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png" alt="Gmail" className="h-6 w-6" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-base font-body">Gmail</CardTitle>
                                        <CardDescription>you@company.com</CardDescription>
                                    </div>
                                </div>
                                <Badge variant="secondary" className="bg-success/10 text-success hover:bg-success/20 border-success/20">
                                    <Check className="h-3 w-3 mr-1" /> Connected
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm text-muted-foreground mb-4">
                                Last synced: 2 minutes ago
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Switch id="gmail-sync" defaultChecked />
                                    <Label htmlFor="gmail-sync" className="font-normal text-sm">Auto-sync emails</Label>
                                </div>
                                <Button variant="outline" size="sm" className="text-muted-foreground">Manage</Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Outlook - Not Connected */}
                    <Card className="opacity-80 hover:opacity-100 transition-opacity">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 bg-white rounded-full border border-border-light flex items-center justify-center p-2">
                                        <img src="https://upload.wikimedia.org/wikipedia/commons/d/df/Microsoft_Office_Outlook_%282018%E2%80%93present%29.svg" alt="Outlook" className="h-6 w-6" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-base font-body">Outlook</CardTitle>
                                        <CardDescription>Office 365 / Exchange</CardDescription>
                                    </div>
                                </div>
                                <Button variant="outline" size="sm" className="h-7 text-xs">
                                    <Plus className="h-3 w-3 mr-1" /> Connect
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground">
                                Connect your Outlook account to sync emails and calendar events.
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <Separator />

            {/* AI Configuration Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-ai/10 rounded-xl flex items-center justify-center text-ai">
                        <Brain className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Intelligence</h2>
                        <p className="text-sm text-ink-light">Configure AI models and API keys</p>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-6 space-y-6">
                        <div className="flex flex-col md:flex-row gap-6">
                            <div className="flex-1 space-y-4">
                                <div className="grid gap-2">
                                    <Label>AI Model</Label>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="border rounded-lg p-3 cursor-pointer bg-primary/5 border-primary ring-1 ring-primary relative">
                                            <div className="absolute top-2 right-2 text-primary">
                                                <Check className="h-4 w-4" />
                                            </div>
                                            <div className="font-medium text-sm">GPT-4o</div>
                                            <div className="text-xs text-muted-foreground">OpenAI (Recommended)</div>
                                        </div>
                                        <div className="border rounded-lg p-3 cursor-pointer hover:bg-paper-mid transition-colors">
                                            <div className="font-medium text-sm">Claude 3.5 Sonnet</div>
                                            <div className="text-xs text-muted-foreground">Anthropic</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="grid gap-2">
                                    <Label htmlFor="api-key">OpenAI API Key</Label>
                                    <div className="flex gap-2">
                                        <Input id="api-key" type="password" defaultValue="sk-........................" className="font-mono text-sm bg-paper" />
                                        <Button variant="outline">Update</Button>
                                    </div>
                                    <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                                        <AlertCircle className="h-3 w-3" />
                                        Key is stored locally and encrypted.
                                    </p>
                                </div>
                            </div>

                            <div className="w-px bg-border-light hidden md:block"></div>

                            <div className="flex-1 space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Draft Autopilot</Label>
                                        <p className="text-xs text-muted-foreground">Automatically generate drafts for incoming emails</p>
                                    </div>
                                    <Switch defaultChecked />
                                </div>
                                <Separator />
                                <div className="flex items-center justify-between">
                                    <div className="space-y-0.5">
                                        <Label className="text-base">Priority Analysis</Label>
                                        <p className="text-xs text-muted-foreground">Analyze and score email priority on arrival</p>
                                    </div>
                                    <Switch defaultChecked />
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </section>

            <Separator />

            {/* Appearance Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center text-slate-700">
                        <Palette className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Appearance</h2>
                        <p className="text-sm text-ink-light">Customize the interface</p>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="font-medium">Interface Theme</p>
                                <p className="text-sm text-muted-foreground">SortMail v1.0 Standard (Light)</p>
                            </div>
                            <Button variant="outline" disabled>Customize (Pro)</Button>
                        </div>
                    </CardContent>
                </Card>
            </section>

        </div>
    );
}
