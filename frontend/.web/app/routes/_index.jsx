import {Fragment,useCallback,useContext,useEffect} from "react"
import {Box as RadixThemesBox,Button as RadixThemesButton,Flex as RadixThemesFlex,Heading as RadixThemesHeading,Text as RadixThemesText} from "@radix-ui/themes"
import {Briefcase as LucideBriefcase,CheckCheck as LucideCheckCheck,Shield as LucideShield,ShieldCheck as LucideShieldCheck,UserCheck as LucideUserCheck,Zap as LucideZap} from "lucide-react"
import {EventLoopContext} from "$/utils/context"
import {ReflexEvent} from "$/utils/state"
import {jsx} from "@emotion/react"




function Button_82c39e6692ac3cee7a4a45e4ce61074b () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_ae98820dbb6962085cb354323d13b78a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.select_role", ({ ["is_client"] : true }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{css:({ ["width"] : "100%", ["cursor"] : "pointer", ["background"] : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", ["color"] : "white", ["&:hover"] : ({ ["transform"] : "translateY(-2px)", ["boxShadow"] : "0 10px 25px rgba(102, 126, 234, 0.4)" }), ["transition"] : "all 0.3s ease" }),onClick:on_click_ae98820dbb6962085cb354323d13b78a,size:"3"},"Get Started")
  )
}


function Button_6b5bdba9ed8ca6396eff22c8eb97c18e () {
  const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_d53f210a48db0f92d029d78b149a1e8e = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.app___states___global_state____global_state.select_role", ({ ["is_client"] : false }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{css:({ ["width"] : "100%", ["cursor"] : "pointer", ["background"] : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", ["color"] : "white", ["&:hover"] : ({ ["transform"] : "translateY(-2px)", ["boxShadow"] : "0 10px 25px rgba(102, 126, 234, 0.4)" }), ["transition"] : "all 0.3s ease" }),onClick:on_click_d53f210a48db0f92d029d78b149a1e8e,size:"3"},"Get Started")
  )
}


export default function Component() {





  return (
    jsx(Fragment,{},jsx(RadixThemesBox,{},jsx(RadixThemesBox,{css:({ ["position"] : "fixed", ["top"] : "0", ["left"] : "0", ["width"] : "100%", ["height"] : "100%", ["background"] : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", ["zIndex"] : "-1" })},),jsx(RadixThemesFlex,{css:({ ["display"] : "flex", ["alignItems"] : "center", ["justifyContent"] : "center", ["minHeight"] : "100vh", ["width"] : "100%" })},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["padding"] : "40px" }),direction:"column",gap:"5"},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["marginBottom"] : "60px" }),direction:"column",gap:"3"},jsx(LucideShieldCheck,{css:({ ["color"] : "white" }),size:60},),jsx(RadixThemesHeading,{css:({ ["color"] : "white", ["fontWeight"] : "700", ["letterSpacing"] : "-0.02em" }),size:"9"},"GigShield"),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "rgba(255, 255, 255, 0.9)", ["textAlign"] : "center", ["maxWidth"] : "600px" }),size:"5"},"Secure Your Gig Work with Blockchain-Powered Escrow")),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",justify:"center",gap:"8",wrap:"wrap"},jsx(RadixThemesBox,{css:({ ["background"] : "white", ["borderRadius"] : "20px", ["boxShadow"] : "0 20px 60px rgba(0, 0, 0, 0.3)", ["width"] : "350px", ["&:hover"] : ({ ["transform"] : "translateY(-8px)", ["boxShadow"] : "0 25px 70px rgba(0, 0, 0, 0.4)" }), ["transition"] : "all 0.3s ease", ["cursor"] : "pointer" })},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["padding"] : "40px" }),direction:"column",gap:"4"},jsx(LucideBriefcase,{css:({ ["color"] : "#667eea" }),size:50},),jsx(RadixThemesHeading,{css:({ ["color"] : "#1a202c", ["fontWeight"] : "600" }),size:"7"},"Login as Client"),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "#4a5568", ["textAlign"] : "center", ["lineHeight"] : "1.6" }),size:"3"},"Post gigs, escrow payments, and verify work completion with AI-powered validation."),jsx(Button_82c39e6692ac3cee7a4a45e4ce61074b,{},))),jsx(RadixThemesBox,{css:({ ["background"] : "white", ["borderRadius"] : "20px", ["boxShadow"] : "0 20px 60px rgba(0, 0, 0, 0.3)", ["width"] : "350px", ["&:hover"] : ({ ["transform"] : "translateY(-8px)", ["boxShadow"] : "0 25px 70px rgba(0, 0, 0, 0.4)" }), ["transition"] : "all 0.3s ease", ["cursor"] : "pointer" })},jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["padding"] : "40px" }),direction:"column",gap:"4"},jsx(LucideUserCheck,{css:({ ["color"] : "#667eea" }),size:50},),jsx(RadixThemesHeading,{css:({ ["color"] : "#1a202c", ["fontWeight"] : "600" }),size:"7"},"Login as Gig Worker"),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "#4a5568", ["textAlign"] : "center", ["lineHeight"] : "1.6" }),size:"3"},"Find gigs, complete tasks, submit proof, and receive instant payments securely."),jsx(Button_6b5bdba9ed8ca6396eff22c8eb97c18e,{},)))),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["marginTop"] : "60px", ["opacity"] : "0.9" }),direction:"column",gap:"3"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",justify:"center",gap:"8",wrap:"wrap"},jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",gap:"2"},jsx(LucideShield,{css:({ ["color"] : "white" }),size:24},),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "white", ["fontWeight"] : "500" }),size:"3"},"Blockchain Security")),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",gap:"2"},jsx(LucideZap,{css:({ ["color"] : "white" }),size:24},),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "white", ["fontWeight"] : "500" }),size:"3"},"Instant Payments")),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",direction:"row",gap:"2"},jsx(LucideCheckCheck,{css:({ ["color"] : "white" }),size:24},),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "white", ["fontWeight"] : "500" }),size:"3"},"AI Verification"))))))),jsx("title",{},"App | Index"),jsx("meta",{content:"favicon.ico",property:"og:image"},))
  )
}