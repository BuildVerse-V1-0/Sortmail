'use client';

import React, { useRef, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { User, Mail, Brain, Palette, Check, Plus, AlertCircle, Save } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api, endpoints } from '@/lib/api';

export default function SettingsPage() {
    const { user, checkSession } = useAuth();
    const nameRef = useRef<HTMLInputElement>(null);
    const [saved, setSaved] = useState(false);

    const queryClient = useQueryClient();

    const updateProfile = useMutation({
        mutationFn: (name: string) =>
            api.patch(endpoints.updateProfile, { name }),
        onSuccess: async () => {
            await checkSession(); // refresh user in AuthContext
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        },
    });

    const handleSave = () => {
        const name = nameRef.current?.value?.trim();
        if (name) updateProfile.mutate(name);
    };

    const initials = user?.name
        ? user.name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2)
        : "?";

    return (
        <div className="space-y-8 pb-20">

            {/* Profile Section */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary">
                        <User className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Profile</h2>
                        <p className="text-sm text-ink-light">Your account information</p>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-6">
                            <Avatar className="h-20 w-20 border-2 border-border-light">
                                {user?.picture && <AvatarImage src={user.picture} />}
                                <AvatarFallback className="bg-primary/5 text-primary text-xl font-display">
                                    {initials}
                                </AvatarFallback>
                            </Avatar>
                            <div className="space-y-4 flex-1 max-w-md">
                                <div className="grid gap-2">
                                    <Label htmlFor="name">Display Name</Label>
                                    <Input ref={nameRef} id="name" defaultValue={user?.name || ""} className="bg-paper" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input id="email" defaultValue={user?.email || ""} disabled className="bg-paper-mid opacity-70" />
                                </div>
                            </div>
                            <div className="ml-auto self-start flex items-center gap-2">
                                {saved && <span className="text-success text-sm flex items-center gap-1"><Check className="w-4 h-4" /> Saved</span>}
                                <Button onClick={handleSave} disabled={updateProfile.isPending} className="gap-2">
                                    <Save className="w-4 h-4" />
                                    {updateProfile.isPending ? "Saving..." : "Save Changes"}
                                </Button>
                            </div>
                        </div>
                        <div className="mt-4 flex gap-3 text-xs text-muted-foreground">
                            <Badge variant="secondary" className="bg-success/10 text-success border-success/20">
                                <Check className="h-3 w-3 mr-1" />
                                Signed in via {user?.provider || "Google"}
                            </Badge>
                            {user?.credits !== undefined && (
                                <Badge variant="secondary">
                                    {user.credits} credits remaining
                                </Badge>
                            )}
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
                        <p className="text-sm text-ink-light">Connected email providers</p>
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
                                        <CardDescription>{user?.email}</CardDescription>
                                    </div>
                                </div>
                                <Badge variant="secondary" className="bg-success/10 text-success hover:bg-success/20 border-success/20">
                                    <Check className="h-3 w-3 mr-1" /> Connected
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent>
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
                            <p className="text-sm text-muted-foreground">Connect your Outlook account to sync emails and calendar events.</p>
                        </CardContent>
                    </Card>
                </div>
            </section>

            <Separator />

            {/* AI Configuration */}
            <section className="space-y-4">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-ai/10 rounded-xl flex items-center justify-center text-ai">
                        <Brain className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-display text-xl text-ink font-semibold">Intelligence</h2>
                        <p className="text-sm text-ink-light">Configure AI behavior</p>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-6 space-y-4">
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
                        <Separator />
                        <div className="flex items-center justify-between">
                            <div className="space-y-0.5">
                                <Label className="text-base">Calendar Detection</Label>
                                <p className="text-xs text-muted-foreground">Detect meeting requests in emails automatically</p>
                            </div>
                            <Switch defaultChecked />
                        </div>
                    </CardContent>
                </Card>
            </section>

            <Separator />

            {/* Appearance */}
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
