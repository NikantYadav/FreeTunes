"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../styles/toastStyles.css';

declare global {
  interface Window {
    phoneEmailReceiver?: (userObj: { user_json_url: string }) => void;
  }
}

export default function SignUp() {
  const serverURL = process.env.NEXT_PUBLIC_SERVER_URL;
  const router = useRouter();
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [nameSubmitted, setNameSubmitted] = useState(false);

  const verifyToken = async (token) => {
    try{
      const response = await fetch(`${serverURL}/model/verify/token`, {
        method : "POST", 
        headers : {
          "Content-Type" : "application/json"
        }, 
        body : JSON.stringify({access_token:token})
      })

      const data = await response.json()

      if(response.ok && data.auth){
        localStorage.setItem("user", JSON.stringify(data.user))
        router.push("/dashboard")
      } else {
      }
    } catch {

    }
  }


    useEffect(()=>{
        const token = Cookies.get("access_token")
        if(token){
        verifyToken(token)
        }
    }, [])

  
    useEffect(() => {
        if (!nameSubmitted) return;
    
        window.phoneEmailReceiver = async ({ user_json_url }) => {
          setIsSubmitting(true);
          try {
            const emailResponse = await fetch(`${serverURL}/model/verify/email/new`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ jsonURL: user_json_url }),
            });
    
            const emailData = await emailResponse.json();
    
            // if (!emailResponse.ok) {
            //   toast.error(emailData.message || "Email verification failed 1.");
            //   return;
            // }
    
            if (!(emailData.verified)) {
              toast.error("Account already exists. Please use Login page.");
              return;
            }

            if(emailData.email){
            const createResponse = await fetch(`${serverURL}/model/create/user`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ email: emailData.email, name: name }),
            });
    
            const createData = await createResponse.json();
            
            if (createResponse.ok && createData.status) {
              Cookies.set("access_token", createData.access_token, { expires: 7 });
              localStorage.setItem("user", JSON.stringify(createData.user));
              toast.success("Account created successfully!");
                setTimeout(() => {
                router.push("/dashboard");
                }, 2500);
              router.push("/dashboard");
            } else {
              toast.error(createData.message || "Failed to create account.");
            }}
          } catch (error) {
            console.error("Verification process failed:", error);
            toast.error("An error occurred during the verification process.");
          } finally {
            setIsSubmitting(false);
          }
        };
    
        const script = document.createElement("script");
        script.src = "https://www.phone.email/verify_email_v1.js";
        script.async = true;
        document.body.appendChild(script);
    
        return () => {
          document.body.removeChild(script);
          delete window.phoneEmailReceiver;
        };
      }, [nameSubmitted, name, router]);

  return (
    <div className="relative min-h-screen overflow-hidden text-white">
      <ToastContainer />
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-indigo-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-full filter blur-[100px] animate-spin-slow"></div>
      </div>

      <div className="relative z-10 mt-5 lg:mt-0">
        <section className="container min-h-screen flex flex-col justify-center items-center gap-8 pb-8 pt-6 md:py-10">
        <motion.div
            className="flex max-w-[980px] flex-col items-center gap-4 text-center"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <motion.h1
              className="text-5xl font-extrabold leading-tight tracking-tighter md:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            >
              Create Your Account
            </motion.h1>
            <motion.p
              className="max-w-[700px] text-xl text-gray-500 mt-2 font-normal"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              Join us and start enjoying free music at your fingertips
            </motion.p>
          </motion.div>

          {!nameSubmitted ? (
            <motion.form
              onSubmit={(e) => {
                e.preventDefault();
                setNameSubmitted(true);
              }}
              className="mt-8 w-full max-w-lg flex flex-col items-center gap-6"
            >
              <input
                type="text"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full p-4 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              <button
                type="submit"
                className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all disabled:opacity-50"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Continuing..." : "Next"}
              </button>
            </motion.form>
          ) : (
            <motion.div className="mt-8 w-full max-w-lg flex flex-col items-center gap-6">
              <div className="pe_verify_email" data-client-id="14032901526356850453"></div>
              <p className="text-gray-400">Check your email for verification</p>
            </motion.div>
          )}

          <motion.div className="mt-6 text-gray-400">
            <Link href="/login" className="flex items-center gap-2">
              <ArrowLeft className="w-5 h-5" />
              Back to Login
            </Link>
          </motion.div>
        </section>
      </div>
    </div>
  );
}
