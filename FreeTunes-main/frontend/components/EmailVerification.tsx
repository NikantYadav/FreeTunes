import { useEffect } from 'react';
import { useRouter } from "next/navigation";
import { toast, ToastContainer } from 'react-toastify';
import Cookies from "js-cookie";

const serverURL = process.env.NEXT_PUBLIC_SERVER_URL;

declare global {
  interface Window {
    phoneEmailReceiver?: (userObj: { user_json_url: string }) => void;
  }
}

const EmailVerification = () => {
  const router = useRouter();

  useEffect(() => {
    window.phoneEmailReceiver = async function (userObj) {
      const user_json_url = userObj.user_json_url;
      try {
        const response = await fetch(`${serverURL}/model/verify/email`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ jsonURL: user_json_url }),
          });

        const data = await response.json();

        if (response.ok && data.verified) {
            Cookies.set("access_token", data.access_token, { expires: 7 });
            localStorage.setItem("user", JSON.stringify(data.user));
            toast.success("Logged in successfully!");
            router.push("/dashboard");
        } else {
            toast.error(data.message || "Verification failed.");
        }
      } catch (error) {
        toast.error("Error verifying OTP. Please try again.");
      }
    };

    const script = document.createElement('script');
    script.src = 'https://www.phone.email/verify_email_v1.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
      delete window.phoneEmailReceiver;
    };
  }, []);

  return (
    <div className="pe_verify_email" data-client-id="14032901526356850453"></div>
  );
};

export default EmailVerification;
