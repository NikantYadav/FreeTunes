"use client";
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../styles/toastStyles.css'
import EmailVerification from "@/components/EmailVerification";

export default function Login() {
    const serverURL = process.env.NEXT_PUBLIC_SERVER_URL;
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [otpSent, setOtpSent] = useState(false);
    const [isOtpValid, setIsOtpValid] = useState(false);
      

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


    // const handleEmailSubmit = async (e: React.FormEvent) => {
    //     e.preventDefault();
    //     setIsSubmitting(true);
    //     try {
    //         const response = await fetch(`${serverURL}/model/generate/otp`, {
    //             method: "POST",
    //             headers: {
    //                 "Content-Type": "application/json",
    //             },
    //             body: JSON.stringify({ email })
    //         });
    //         if (response.ok) {
    //             const data = await response.json();
    //             if (data.generated === true) {
    //                 setOtpSent(true);
    //                 toast.success("OTP sent to your email.");
    //             }
    //         } else {
    //             throw new Error("Failed to generate OTP. Please try again.");
    //         }
    //     } catch (error) {
    //         toast.error(error.message);
    //     } finally {
    //         setIsSubmitting(false);
    //     }
    // };

    
    // const handleOtpSubmit = async (e: React.FormEvent) => {
    //     e.preventDefault();
    //     setIsSubmitting(true);
    //     try {
    //         const response = await fetch(`${serverURL}/model/verify/otp`, {
    //             method: "POST",
    //             headers: {
    //                 "Content-Type": "application/json",
    //             },
    //             body: JSON.stringify({ email, otp })
    //         });
    //         const data = await response.json();
    //         if (response.ok && data.verified) {
    //             Cookies.set("access_token", data.access_token, { expires: 7 });
    //             localStorage.setItem("user", JSON.stringify(data.user));
    //             toast.success("Logged in successfully!");
    //             router.push("/dashboard");
    //         } else {
    //             toast.error(data.message);
    //         }
    //     } catch (error) {
    //         toast.error("Error verifying OTP. Please try again.");
    //     } finally {
    //         setIsSubmitting(false);
    //     }
    // };

    return (
        <div className="relative min-h-screen overflow-hidden text-white">
            <ToastContainer />
            {/* Enhanced background elements */}
            <div className="absolute inset-0 overflow-hidden">
               <div className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-indigo-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
               <div className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
               <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-full filter blur-[100px] animate-spin-slow"></div>
           </div>
           {/* Content */}
           <div className="relative z-10 mt-5 lg:mt-0">
               <section className="container min-h-screen flex flex-col justify-center items-center gap-8 pb-8 pt-6 md:py-10">
                   <motion.div className="flex max-w-[980px] flex-col items-center gap-4 text-center" initial={{ opacity: 0, y: -50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: "easeOut" }}>
                       <motion.h1 className="text-5xl font-extrabold leading-tight tracking-tighter md:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}>
                           Login to Your Account
                       </motion.h1>
                       <motion.h1>
                        <EmailVerification />
                       </motion.h1>

                       {/* <motion.p className="max-w-[700px] text-xl text-gray-500 mt-2 font-normal" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8, delay: 0.6 }}>
                           Enter your email to receive an OTP for login.
                       </motion.p> */}
                       
                   </motion.div>

                   {/* Email Input Form */}
                   {/* {!otpSent && !isOtpValid && (
                       <motion.form onSubmit={handleEmailSubmit} className="mt-8 w-full max-w-lg flex flex-col items-center gap-6" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 1 }}>
                           <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-4 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                           <button type="submit" className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all disabled:opacity-50" disabled={isSubmitting}>
                               {isSubmitting ? "Sending OTP..." : "Send OTP"}
                           </button>
                       </motion.form>
                   )} */}

                   {/* OTP Validation Form */}
                   {/* {otpSent && !isOtpValid && (
                       <motion.form onSubmit={handleOtpSubmit} className="mt-8 w-full max-w-lg flex flex-col items-center gap-6" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 1 }}>
                           <input type="text" placeholder="Enter OTP" value={otp} onChange={(e) => setOtp(e.target.value)} className="w-full p-4 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                           <button type="submit" className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all disabled:opacity-50" disabled={isSubmitting}>
                               {isSubmitting ? "Verifying OTP..." : "Verify OTP"}
                           </button>
                       </motion.form>
                   )} */}

                   {/* Back to Sign Up Link */}
                   <motion.div className="mt-6 text-gray-400" initial={{ opacity: 0, y: 50 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 1.2 }}>
                       <Link href="/signup" className="flex items-center gap-2">
                           <ArrowLeft className="w-5 h=5" /> Back to Sign Up
                       </Link>
                   </motion.div>
               </section>
           </div>
       </div>
   );
}

