import asyncio

import constants
import streamlit as st
from csp_tools import CSPExtractor, CSPGenerator, MCPCSPRunner


def handle_model_selection():
    selected_model = st.session_state["model_key"]
    print("it changes", selected_model)
    parse_split = selected_model.split("[")
    model = parse_split[1].replace("]", "").strip()
    brand = parse_split[0].strip()
    st.session_state.code_generator = CSPGenerator(model, brand)
    # if len(st.session_state.code_generator.get_error_messages()) != 0:
    #     for msg in st.session_state.code_generator.get_error_messages():
    #         st.warning(msg)
    # return


# Streamlit App
def main():

    st.set_page_config(
        page_title="CSP Problem Solver with LLM", page_icon="🧩", layout="wide"
    )
    st.title("🧩 Constraint Programming with LLM")
    st.markdown("Solve constraint programming problems using LLM")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Paramètres du modèle
    st.sidebar.subheader("🎛️ Model parameter")

    model = st.sidebar.selectbox(
        "Model",
        constants.MODELS,
        index=1,
        key="model_key",
        on_change=handle_model_selection,
    )
    parse_split = model.split("[")
    st.session_state.model = parse_split[1].replace("]", "").strip()
    st.session_state.brand = parse_split[0].strip()

    st.subheader(
        f"Selected model is {st.session_state.model} from {st.session_state.brand} provider"
    )

    # Initialize components
    if "code_generator" not in st.session_state:
        st.session_state.code_generator = CSPGenerator(
            st.session_state.model, st.session_state.brand
        )
    if len(st.session_state.code_generator.get_error_messages()) != 0:
        for msg in st.session_state.code_generator.get_error_messages():
            st.warning(msg)
        return

    if "mcp_runner" not in st.session_state:
        st.session_state.mcp_runner = MCPCSPRunner()

    if "extractor" not in st.session_state:
        st.session_state.extractor = CSPExtractor()

    # Main interface
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Problem Description")

        selected_example = st.selectbox(
            "Choose an example or custom:", list(constants.EXAMPLE_PROBLEMS.keys())
        )

        if selected_example == "Custom":
            problem_description = st.text_area(
                "Describe your constraint programming problem:",
                height=150,
                placeholder="Example: Place 4 queens on a 4x4 chessboard...",
            )
        else:
            problem_description = st.text_area(
                "Problem Description:",
                value=constants.EXAMPLE_PROBLEMS[selected_example],
                height=150,
            )

        # Generate button
        generate_col1, generate_col2 = st.columns([1, 1])
        stream_mode = True
        # with generate_col1:
        #     stream_mode = st.checkbox(
        #         "🔄 Stream Response",
        #         value=True,
        #         help="Show Claude's response in real-time",
        #     )

        # with generate_col2:
        if st.button("🤖 Generate CSP Code with LLM", type="primary"):
            if problem_description:
                if stream_mode:
                    # Streaming mode with proper async handling
                    st.markdown("### 🔄 LLM is generating code...")

                    # Create container for streaming response
                    streaming_container = st.container()

                    # Create and run async task for streaming
                    async def run_streaming_generation():
                        return await st.session_state.code_generator.generate_csp_code_stream_async(
                            problem_description, streaming_container
                        )

                    # Execute the async streaming function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        with st.spinner("LLM is generating code..."):
                            llm_response = loop.run_until_complete(
                                run_streaming_generation()
                            )

                        # Extract PyCSP3 code
                        extracted_code = st.session_state.extractor.extract_pycsp3_code(
                            llm_response
                        )

                        # Store in session state
                        st.session_state.generated_code = extracted_code
                        st.session_state.llm_response = llm_response

                        st.success(
                            "✅ Code generated successfully with async streaming!"
                        )
                    except Exception as e:
                        st.error(f"❌ Streaming generation failed: {str(e)}")
                    finally:
                        loop.close()

                else:
                    # Non-streaming mode with async
                    with st.spinner("Generating PyCSP3 code with LLM..."):
                        # Create and run async task for non-streaming
                        async def run_standard_generation():
                            return await st.session_state.code_generator.generate_csp_code_async(
                                problem_description
                            )

                        # Execute the async function
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            llm_response = loop.run_until_complete(
                                run_standard_generation()
                            )

                            # Extract PyCSP3 code
                            extracted_code = (
                                st.session_state.extractor.extract_pycsp3_code(
                                    llm_response
                                )
                            )

                            # Store in session state
                            st.session_state.generated_code = extracted_code
                            st.session_state.llm_response = llm_response

                            st.success("✅ Code generated successfully with async!")
                        except Exception as e:
                            st.error(f"❌ Generation failed: {str(e)}")
                        finally:
                            loop.close()
            else:
                st.error("Please enter a problem description.")

    with col2:
        st.header("Generated PyCSP3 Code")

        if "generated_code" in st.session_state:
            # Show final generated code in a clean format
            st.subheader("📋 Final Generated Code")
            st.code(st.session_state.generated_code, language="python")

            # Show raw Claude response in expander
            with st.expander("🤖 View Full LLM Response"):
                st.text(st.session_state.llm_response)

            # Edit code option
            if st.checkbox("✏️ Edit code before execution"):
                edited_code = st.text_area(
                    "Edit the generated code:",
                    value=st.session_state.generated_code,
                    height=300,
                    key="code_editor",
                )
                execution_code = edited_code
            else:
                execution_code = st.session_state.generated_code

            # Execution controls
            st.subheader("🚀 Execution Controls")

            col2_1, col2_2, col2_3 = st.columns([1, 1, 1])

            with col2_1:
                if st.button("🔧 Execute via MCP", type="secondary"):
                    with st.spinner("Executing CSP code via MCP..."):
                        # Create real-time execution container
                        execution_container = st.container()
                        execution_status = execution_container.empty()
                        execution_progress = execution_container.progress(0)

                        # Update progress
                        execution_status.info("🔄 Initializing MCP runner...")
                        execution_progress.progress(25)

                        # Run code through MCP
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            # Initialize MCP if needed
                            execution_status.info("🔄 Setting up MCP session...")
                            execution_progress.progress(50)

                            if (
                                not hasattr(st.session_state.mcp_runner, "session")
                                or not st.session_state.mcp_runner.session
                            ):
                                loop.run_until_complete(
                                    st.session_state.mcp_runner.initialize_mcp()
                                )

                            # Execute code
                            execution_status.info("🔄 Executing CSP code...")
                            execution_progress.progress(75)

                            result = loop.run_until_complete(
                                st.session_state.mcp_runner.run_csp_code(execution_code)
                            )

                            execution_progress.progress(100)
                            execution_status.success("✅ Execution completed!")

                            st.session_state.execution_result = result

                        except Exception as e:
                            execution_status.error(f"❌ Execution failed: {str(e)}")
                            st.session_state.execution_result = {
                                "success": False,
                                "output": "",
                                "error": str(e),
                                "code": execution_code,
                            }
                        finally:
                            loop.close()

            with col2_2:
                if st.button("💾 Save Code"):
                    # Create download link for the code
                    st.download_button(
                        label="📥 Download PyCSP3 Code",
                        data=execution_code,
                        file_name=f"csp_problem_{len(execution_code)}.py",
                        mime="text/plain",
                    )

            with col2_3:
                if st.button("🔄 Reset"):
                    # Clear session state
                    for key in [
                        "generated_code",
                        "llm_response",
                        "execution_result",
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

        else:
            st.info("👈 Generate code first using the button on the left.")

            # Show placeholder for streaming
            if st.session_state.get("show_streaming_placeholder", False):
                st.markdown("### 🔄 Streaming Response Preview")
                st.code(
                    "# Claude's response will appear here in real-time...",
                    language="python",
                )

    # Results section
    if "execution_result" in st.session_state:
        st.header("🎯 Execution Results")

        result = st.session_state.execution_result

        # Create columns for results
        result_col1, result_col2 = st.columns([2, 1])

        with result_col1:
            if result["success"]:
                st.success("✅ Code executed successfully!")

                if result["output"]:
                    st.subheader("📊 Solution Output:")
                    # Try to format the output nicely
                    output_lines = result["output"].strip().split("\n")
                    for line in output_lines:
                        if line.strip():
                            if "Solution:" in line or "Result:" in line:
                                st.markdown(f"**{line}**")
                            else:
                                st.text(line)
                else:
                    st.info("Code executed but produced no output.")
            else:
                st.error("❌ Execution failed!")

                if result["error"]:
                    st.subheader("🚨 Error Details:")
                    st.code(result["error"], language="text")

        with result_col2:
            # Execution metrics
            st.subheader("📈 Execution Info")

            # Create metrics
            if result["success"]:
                st.metric("Status", "✅ Success", delta="Solved")
            else:
                st.metric("Status", "❌ Failed", delta="Error")

            # Code length metric
            code_lines = len(result["code"].split("\n"))
            st.metric("Code Lines", code_lines)

            # Show execution time if available (placeholder)
            st.metric("Runtime", "< 1s", delta="Fast")

        # Show detailed execution info in expander
        with st.expander("🔍 Detailed Execution Information"):
            st.json(
                {
                    "success": result["success"],
                    "output_length": len(result["output"]) if result["output"] else 0,
                    "error_present": bool(result["error"]),
                    "code_length": len(result["code"]),
                }
            )

            # Show the actual executed code
            st.subheader("Executed Code:")
            st.code(result["code"], language="python")

    # Real-time streaming demo section
    st.markdown("---")
    st.header("🔄 Real-time Streaming Demo")

    demo_col1, demo_col2 = st.columns([1, 1])

    with demo_col1:
        st.subheader("Try Quick Examples")
        quick_examples = [
            "3x3 magic square",
            "Simple graph coloring",
            "Coin change problem",
            "Assignment problem",
        ]

        selected_quick = st.selectbox("Quick examples:", ["Select..."] + quick_examples)

        if selected_quick != "Select..." and st.button("🚀 Generate Quickly"):
            st.session_state.show_streaming_placeholder = True
            # Auto-fill and trigger generation
            quick_descriptions = {
                "3x3 magic square": "Create a 3x3 magic square where all rows, columns, and diagonals sum to 15",
                "Simple graph coloring": "Color a triangle graph (3 nodes, all connected) with minimum colors",
                "Coin change problem": "Find ways to make change for 10 cents using coins [1,5,10]",
                "Assignment problem": "Assign 3 tasks to 3 workers with cost matrix [[1,2,3],[2,1,3],[3,2,1]]",
            }

            if selected_quick in quick_descriptions:
                with st.container():
                    st.markdown("### 🔄 Streaming Claude's Response...")
                    streaming_container = st.container()

                    # Run async streaming in a proper event loop
                    async def run_quick_generation():
                        return await st.session_state.code_generator.generate_csp_code_stream_async(
                            quick_descriptions[selected_quick], streaming_container
                        )

                    # Execute the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        llm_response = loop.run_until_complete(run_quick_generation())

                        extracted_code = st.session_state.extractor.extract_pycsp3_code(
                            llm_response
                        )
                        st.session_state.generated_code = extracted_code
                        st.session_state.llm_response = llm_response

                        st.success("✅ Quick example generated!")
                    finally:
                        loop.close()

    with demo_col2:
        st.subheader("Streaming Features")
        st.markdown(
            """
        🔄 **Real-time Response**: See LLM's code generation live
        
        📝 **Chunk-by-chunk Display**: Each token appears as it's generated
        
        ⚡ **Immediate Feedback**: No waiting for complete response
        
        🎯 **Better UX**: Visual progress indication
        
        🔧 **Error Handling**: Graceful handling of streaming interruptions
        """
        )

        # Show streaming status
        if st.session_state.get("show_streaming_placeholder", False):
            st.info("🔄 Streaming mode is active")
        else:
            st.info("💤 Streaming mode is ready")

    # Footer with instructions
    st.markdown("---")
    st.markdown(
        """
    ### How to use:
    1. **Configure**: Enter your Local Model API key in the sidebar
    2. **Describe**: Choose an example problem or describe your own constraint programming problem
    3. **Generate**: Click "Generate CSP Code with LLM" to create PyCSP3 code
    4. **Execute**: Run the generated code through MCP functions
    5. **Review**: Check the results and download the code if needed
    
    ### Requirements:
    ```bash
    pip install mcp openai pycsp3 streamlit
    ```
    
    
    """
    )
